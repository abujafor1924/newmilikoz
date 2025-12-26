# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Book
from .serializers import BookSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

class BookListView(APIView):
    """
    GET: List all books
    POST: Create a new book
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET method - সব বইয়ের লিস্ট দেখাবে
        Query Parameters:
        - search: Search by title or author
        - min_price: Minimum price
        - max_price: Maximum price
        - available: Filter by availability
        """
        books = Book.objects.all()
        
        # Filtering - Query Parameters
        search_query = request.GET.get('search')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        available = request.GET.get('available')
        
        if search_query:
            books = books.filter(
                models.Q(title__icontains=search_query) |
                models.Q(author__icontains=search_query)
            )
        
        if min_price:
            books = books.filter(price__gte=min_price)
        
        if max_price:
            books = books.filter(price__lte=max_price)
        
        if available is not None:
            is_available = available.lower() in ['true', '1', 'yes']
            books = books.filter(is_available=is_available)
        
        # Ordering
        order_by = request.GET.get('order_by', 'title')
        if order_by in ['title', 'author', 'price', 'published_date']:
            books = books.order_by(order_by)
        
        # Pagination (Manual)
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Page size
        paginator.page_query_param = 'page'
        paginated_books = paginator.paginate_queryset(books, request)
        
        serializer = BookSerializer(paginated_books, many=True)
        
        # Custom response with metadata
        return paginator.get_paginated_response({
            "success": True,
            "message": "Books retrieved successfully",
            "data": serializer.data,
            "metadata": {
                "total_books": books.count(),
                "page_size": paginator.page_size,
                "current_page": paginator.page.number if hasattr(paginator, 'page') else 1
            }
        })
    
    def post(self, request):
        """
        POST method - নতুন বই create করবে
        Request Body:
        {
            "title": "Book Title",
            "author": "Author Name",
            "price": 29.99,
            "published_date": "2024-01-15",
            "is_available": true
        }
        """
        serializer = BookSerializer(data=request.data)
        
        if serializer.is_valid():
            # Extra validation (Business Logic)
            if float(request.data.get('price', 0)) <= 0:
                return Response({
                    "success": False,
                    "message": "Price must be greater than 0",
                    "errors": {"price": ["Price must be positive"]}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Save with additional data
            book = serializer.save()
            
            # Success response
            return Response({
                "success": True,
                "message": "Book created successfully",
                "data": serializer.data,
                "book_id": book.id
            }, status=status.HTTP_201_CREATED)
        
        # Error response
        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

        class BookDetailView(APIView):
    """
    GET: Get single book details
    PUT: Update entire book (all fields required)
    PATCH: Partially update book
    DELETE: Delete a book
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """Helper method to get book object or return 404"""
        return get_object_or_404(Book, pk=pk)
    
    def get(self, request, pk):
        """
        GET method - একটি বইয়ের details দেখাবে
        URL: /api/books/<id>/
        """
        try:
            book = self.get_object(pk)
            serializer = BookSerializer(book)
            
            # You can add additional data
            additional_data = {
                "status": "available" if book.is_available else "not available",
                "formatted_price": f"${book.price}",
                "days_since_published": (date.today() - book.published_date).days
            }
            
            return Response({
                "success": True,
                "message": "Book details retrieved successfully",
                "data": serializer.data,
                "additional_info": additional_data
            })
            
        except Book.DoesNotExist:
            return Response({
                "success": False,
                "message": f"Book with id {pk} not found"
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        """
        PUT method - পুরো বই update করবে (সব field required)
        Request Body: All book fields required
        """
        try:
            book = self.get_object(pk)
            serializer = BookSerializer(book, data=request.data)
            
            if serializer.is_valid():
                # Business logic validation
                if 'price' in request.data and float(request.data['price']) <= 0:
                    return Response({
                        "success": False,
                        "message": "Price must be greater than 0"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Book updated successfully",
                    "data": serializer.data
                })
            
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Book.DoesNotExist:
            return Response({
                "success": False,
                "message": f"Book with id {pk} not found"
            }, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        """
        PATCH method - কিছু fields update করবে
        Request Body: Only fields to update
        """
        try:
            book = self.get_object(pk)
            serializer = BookSerializer(book, data=request.data, partial=True)
            
            if serializer.is_valid():
                # Custom validation before saving
                if 'price' in request.data:
                    new_price = float(request.data['price'])
                    if new_price <= 0:
                        return Response({
                            "success": False,
                            "message": "Price must be greater than 0"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Track price changes
                    if new_price != book.price:
                        print(f"Price changed from {book.price} to {new_price}")
                
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Book updated partially",
                    "data": serializer.data,
                    "updated_fields": list(request.data.keys())
                })
            
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Book.DoesNotExist:
            return Response({
                "success": False,
                "message": f"Book with id {pk} not found"
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        """
        DELETE method - বই delete করবে
        URL: /api/books/<id>/
        """
        try:
            book = self.get_object(pk)
            
            # Check if book can be deleted (business logic)
            if not book.is_available:
                return Response({
                    "success": False,
                    "message": "Cannot delete unavailable book. Mark as available first."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Store data before deletion if needed
            deleted_data = {
                "title": book.title,
                "author": book.author,
                "deleted_at": timezone.now()
            }
            
            book.delete()
            
            return Response({
                "success": True,
                "message": f"Book '{book.title}' deleted successfully",
                "deleted_book": deleted_data
            }, status=status.HTTP_200_OK)
            
        except Book.DoesNotExist:
            return Response({
                "success": False,
                "message": f"Book with id {pk} not found"
            }, status=status.HTTP_404_NOT_FOUND)


class BookOperationsView(APIView):
    """
    Custom operations beyond basic CRUD
    """
    permission_classes = [IsAuthenticated]
    
    # POST for custom actions
    def post(self, request, pk=None):
        """Handle multiple custom operations"""
        action = request.data.get('action')
        
        if not action:
            return Response({
                "success": False,
                "message": "Action is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'bulk_delete':
            return self.bulk_delete(request)
        elif action == 'update_price':
            return self.update_price(request, pk)
        elif action == 'toggle_availability':
            return self.toggle_availability(request, pk)
        else:
            return Response({
                "success": False,
                "message": f"Unknown action: {action}"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def bulk_delete(self, request):
        """Delete multiple books at once"""
        book_ids = request.data.get('book_ids', [])
        
        if not book_ids:
            return Response({
                "success": False,
                "message": "No book IDs provided"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        books = Book.objects.filter(id__in=book_ids)
        deleted_count = books.count()
        
        # Store deleted books info
        deleted_books_info = list(books.values('id', 'title'))
        
        books.delete()
        
        return Response({
            "success": True,
            "message": f"{deleted_count} books deleted successfully",
            "deleted_books": deleted_books_info
        })
    
    def update_price(self, request, pk):
        """Custom price update with validation"""
        try:
            book = get_object_or_404(Book, pk=pk)
            new_price = request.data.get('new_price')
            discount_percent = request.data.get('discount_percent')
            
            if new_price:
                # Direct price update
                book.price = float(new_price)
            elif discount_percent:
                # Apply discount
                discount = float(discount_percent)
                if discount < 0 or discount > 100:
                    return Response({
                        "success": False,
                        "message": "Discount must be between 0 and 100"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                original_price = book.price
                book.price = original_price * (1 - discount/100)
            
            # Additional validation
            if book.price <= 0:
                return Response({
                    "success": False,
                    "message": "Price must be greater than 0"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            book.save()
            
            return Response({
                "success": True,
                "message": "Price updated successfully",
                "old_price": float(original_price) if 'original_price' in locals() else None,
                "new_price": float(book.price),
                "discount_applied": discount_percent if discount_percent else None
            })
            
        except Book.DoesNotExist:
            return Response({
                "success": False,
                "message": "Book not found"
            }, status=status.HTTP_404_NOT_FOUND)
    
    def toggle_availability(self, request, pk):
        """Toggle book availability"""
        try:
            book = get_object_or_404(Book, pk=pk)
            book.is_available = not book.is_available
            book.save()
            
            status_text = "available" if book.is_available else "not available"
            
            return Response({
                "success": True,
                "message": f"Book is now {status_text}",
                "book_id": book.id,
                "current_status": status_text
            })
            
        except Book.DoesNotExist:
            return Response({
                "success": False,
                "message": "Book not found"
            }, status=status.HTTP_404_NOT_FOUND)


class BookSearchView(APIView):
    """Advanced search functionality"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Advanced search with multiple criteria"""
        books = Book.objects.all()
        
        # Multiple search parameters
        params = {
            'title': request.GET.get('title'),
            'author': request.GET.get('author'),
            'min_price': request.GET.get('min_price'),
            'max_price': request.GET.get('max_price'),
            'published_after': request.GET.get('published_after'),
            'published_before': request.GET.get('published_before'),
            'available': request.GET.get('available'),
            'search': request.GET.get('search')  # General search
        }
        
        # Apply filters
        if params['title']:
            books = books.filter(title__icontains=params['title'])
        
        if params['author']:
            books = books.filter(author__icontains=params['author'])
        
        if params['min_price']:
            books = books.filter(price__gte=params['min_price'])
        
        if params['max_price']:
            books = books.filter(price__lte=params['max_price'])
        
        if params['published_after']:
            books = books.filter(published_date__gte=params['published_after'])
        
        if params['published_before']:
            books = books.filter(published_date__lte=params['published_before'])
        
        if params['available']:
            is_available = params['available'].lower() in ['true', '1', 'yes']
            books = books.filter(is_available=is_available)
        
        if params['search']:
            books = books.filter(
                models.Q(title__icontains=params['search']) |
                models.Q(author__icontains=params['search'])
            )
        
        # Sorting
        sort_by = request.GET.get('sort_by', 'title')
        sort_order = request.GET.get('sort_order', 'asc')
        
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        
        books = books.order_by(sort_by)
        
        serializer = BookSerializer(books, many=True)
        
        # Statistics
        total_books = books.count()
        total_price = sum(book.price for book in books)
        average_price = total_price / total_books if total_books > 0 else 0
        
        return Response({
            "success": True,
            "message": f"Found {total_books} books",
            "data": serializer.data,
            "statistics": {
                "total_books": total_books,
                "total_price": float(total_price),
                "average_price": float(average_price),
                "available_books": books.filter(is_available=True).count(),
                "unavailable_books": books.filter(is_available=False).count()
            },
            "search_params": {k: v for k, v in params.items() if v}
        })

<!-- 
        # urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Basic CRUD endpoints
    path('books/', views.BookListView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail-update-delete'),
    
    # Custom operations
    path('books/operations/', views.BookOperationsView.as_view(), name='book-operations'),
    path('books/operations/<int:pk>/', views.BookOperationsView.as_view(), name='book-specific-operations'),
    
    # Search
    path('books/search/', views.BookSearchView.as_view(), name='book-search'),
] -->