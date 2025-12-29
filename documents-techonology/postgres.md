I'll guide you through PostgreSQL setup with Django, connections, and creating visualizations.

## **1. PostgreSQL Setup with Django**

### **Installation & Configuration**

```bash
# Install required packages
pip install django psycopg2 psycopg2-binary pandas matplotlib seaborn plotly

# Or with poetry/pipenv
pip install django psycopg2 pandas plotly django-plotly-dash
```

### **Update Django Settings**

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# For Docker PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres',
#         'USER': 'postgres',
#         'PASSWORD': 'postgres',
#         'HOST': 'db',  # Docker service name
#         'PORT': '5432',
#     }
# }
```

### **Docker Compose (Recommended)**

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydatabase
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    ports:
      - "5432:5432"
  
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgres://myuser:mypassword@db:5432/mydatabase

volumes:
  postgres_data:
```

## **2. Accessing PostgreSQL Data in Django**

### **Using Django ORM**

```python
# models.py
from django.db import models

class SalesData(models.Model):
    date = models.DateField()
    product = models.CharField(max_length=100)
    quantity = models.IntegerField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    region = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'sales_data'  # If using existing table

# Query data
from .models import SalesData
import pandas as pd

def get_data_as_dataframe():
    # Get all data
    queryset = SalesData.objects.all()
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(list(queryset.values()))
    return df

# Aggregated queries
from django.db.models import Sum, Avg, Count

def aggregated_data():
    # Group by region
    region_data = SalesData.objects.values('region').annotate(
        total_revenue=Sum('revenue'),
        avg_quantity=Avg('quantity'),
        count=Count('id')
    )
    return pd.DataFrame(list(region_data))
```

### **Direct SQL Connection (for complex queries)**

```python
# views.py
from django.db import connection
import pandas as pd

def execute_sql_query(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
    
    df = pd.DataFrame(data, columns=columns)
    return df

# Example usage
query = """
SELECT 
    region,
    product,
    SUM(revenue) as total_revenue,
    AVG(quantity) as avg_quantity
FROM sales_data
WHERE date >= '2024-01-01'
GROUP BY region, product
ORDER BY total_revenue DESC
"""
df = execute_sql_query(query)
```

## **3. Visualization Options**

### **Option 1: Plotly (Interactive & Easy)**

```python
# views.py
import plotly.express as px
import plotly.graph_objects as go
from django.shortcuts import render

def sales_dashboard(request):
    df = get_data_as_dataframe()
    
    # 1. Bar Chart - Revenue by Region
    fig1 = px.bar(
        df.groupby('region')['revenue'].sum().reset_index(),
        x='region',
        y='revenue',
        title='Revenue by Region',
        color='region'
    )
    
    # 2. Line Chart - Revenue Trend
    fig2 = px.line(
        df.groupby('date')['revenue'].sum().reset_index(),
        x='date',
        y='revenue',
        title='Revenue Trend Over Time'
    )
    
    # 3. Pie Chart - Product Distribution
    fig3 = px.pie(
        df.groupby('product').size().reset_index(name='count'),
        values='count',
        names='product',
        title='Product Distribution'
    )
    
    # 4. Scatter Plot
    fig4 = px.scatter(
        df,
        x='quantity',
        y='revenue',
        color='region',
        size='revenue',
        hover_data=['product'],
        title='Quantity vs Revenue'
    )
    
    context = {
        'fig1': fig1.to_html(),
        'fig2': fig2.to_html(),
        'fig3': fig3.to_html(),
        'fig4': fig4.to_html(),
    }
    
    return render(request, 'dashboard.html', context)
```

### **Option 2: Django-Plotly-Dash (Embedded Dashboards)**

```python
# Install: pip install django-plotly-dash

# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
]

# Create dash app
# dash_apps.py
import dash
from dash import dcc, html
import plotly.express as px
from django_plotly_dash import DjangoDash

app = DjangoDash('SalesDashboard')

app.layout = html.Div([
    html.H1('Sales Dashboard'),
    dcc.Graph(id='revenue-chart'),
    dcc.Dropdown(
        id='region-selector',
        options=[{'label': r, 'value': r} for r in regions],
        multi=True
    ),
    dcc.DatePickerRange(
        id='date-range'
    )
])

# In template
{% load plotly_dash %}
{% plotly_app name="SalesDashboard" %}
```

### **Option 3: Matplotlib/Seaborn (Static Charts)**

```python
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

def generate_matplotlib_chart(df):
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='region', y='revenue')
    plt.title('Revenue by Region')
    plt.xticks(rotation=45)
    
    # Save to base64 for HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(image_png).decode('utf-8')
    return graphic

# In view
def chart_view(request):
    df = get_data_as_dataframe()
    chart = generate_matplotlib_chart(df)
    return render(request, 'chart.html', {'chart': chart})
```

## **4. Easy Visualization Templates**

### **dashboard.html**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .chart-container {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <h1>Sales Dashboard</h1>
    
    <div class="dashboard-grid">
        <div class="chart-container">
            {{ fig1|safe }}
        </div>
        <div class="chart-container">
            {{ fig2|safe }}
        </div>
        <div class="chart-container">
            {{ fig3|safe }}
        </div>
        <div class="chart-container">
            {{ fig4|safe }}
        </div>
    </div>
</body>
</html>
```

## **5. Quick Start Utility Functions**

```python
# utils/visualization.py
import pandas as pd
import plotly.express as px
from django.db import connection

class DjangoVisualizer:
    def __init__(self):
        self.connection = connection
    
    def query_to_dataframe(self, sql_query):
        """Execute SQL and return DataFrame"""
        return pd.read_sql_query(sql_query, self.connection)
    
    def model_to_dataframe(self, model_queryset):
        """Convert Django queryset to DataFrame"""
        return pd.DataFrame(list(model_queryset.values()))
    
    def create_bar_chart(self, df, x_col, y_col, title="", **kwargs):
        """Quick bar chart"""
        return px.bar(df, x=x_col, y=y_col, title=title, **kwargs)
    
    def create_line_chart(self, df, x_col, y_col, title="", **kwargs):
        """Quick line chart"""
        return px.line(df, x=x_col, y=y_col, title=title, **kwargs)
    
    def create_pie_chart(self, df, names_col, values_col, title=""):
        """Quick pie chart"""
        return px.pie(df, names=names_col, values=values_col, title=title)
    
    def dashboard_from_sql(self, sql_queries):
        """Create dashboard from multiple SQL queries"""
        charts = {}
        for name, query in sql_queries.items():
            df = self.query_to_dataframe(query)
            # Auto-detect chart type based on data
            if len(df) > 10:
                chart = self.create_line_chart(df, df.columns[0], df.columns[1])
            else:
                chart = self.create_bar_chart(df, df.columns[0], df.columns[1])
            charts[name] = chart.to_html()
        return charts

# Usage
viz = DjangoVisualizer()
dashboard = viz.dashboard_from_sql({
    'revenue_by_region': 'SELECT region, SUM(revenue) FROM sales GROUP BY region',
    'monthly_trend': 'SELECT month, SUM(revenue) FROM sales GROUP BY month'
})
```

## **6. Performance Tips**

```python
# Use database-side aggregation
# Instead of:
df = pd.DataFrame(list(SalesData.objects.all().values()))
grouped = df.groupby('region')['revenue'].sum()

# Do:
from django.db.models import Sum
data = SalesData.objects.values('region').annotate(
    total_revenue=Sum('revenue')
)
df = pd.DataFrame(list(data))

# Use .iterator() for large datasets
large_qs = SalesData.objects.all().iterator(chunk_size=2000)
for chunk in large_qs:
    process_chunk(chunk)

# Create database views for complex queries
# In migration:
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = []
    
    operations = [
        migrations.RunSQL("""
            CREATE VIEW sales_summary AS
            SELECT 
                region,
                product,
                DATE_TRUNC('month', date) as month,
                SUM(revenue) as total_revenue,
                COUNT(*) as transactions
            FROM sales_data
            GROUP BY region, product, DATE_TRUNC('month', date)
        """)
    ]
```

## **7. Deployment Considerations**

```python
# Use connection pooling
# Install: pip install django-db-connections-pool

# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.postgresql',
        'NAME': 'db_name',
        'POOL_OPTIONS': {
            'POOL_SIZE': 10,
            'MAX_OVERFLOW': 20,
            'RECYCLE': 3600,
        }
    }
}

# Cache expensive queries
from django.core.cache import cache
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def dashboard_view(request):
    # Your view logic
    pass
```

This setup gives you a complete visualization pipeline from PostgreSQL to interactive dashboards. Start with Plotly for quick interactive charts, and consider Django-Plotly-Dash for more complex dashboard requirements.