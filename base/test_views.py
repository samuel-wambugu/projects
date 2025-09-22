from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import CustomUser, MediaFiles, Thumbnail, Comments
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Set up URLs
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')
        self.register_url = reverse('register')
        self.upload_video_url = reverse('upload_video')
        self.upload_thumbnail_url = reverse('upload_thumbnail')

        # Create a test user
        self.user_password = 'testpass123'
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com',
            password=self.user_password,
            fullname='Test User',
            phonenumber='+254700000001'  # Use a unique phone number
        )

        # Create test video file
        self.video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )

        # Create test image file
        self.image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
    
    def test_login_page_GET(self):
        """Test GET request to login page"""
        response = self.client.get(self.login_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/loginpage.html')
        self.assertEqual(response.context['page'], 'login')
    
    def test_authenticated_user_redirect(self):
        """Test that authenticated users are redirected to dashboard"""
        # First login the user
        self.client.login(username=self.user.email, password=self.user_password)
        
        # Try accessing login page
        response = self.client.get(self.login_url)
        
        self.assertRedirects(response, self.dashboard_url)
    
    def test_successful_login(self):
        """Test successful login with valid credentials"""
        response = self.client.post(self.login_url, {
            'Email': 'testuser@example.com',
            'Password': self.user_password
        })
        
        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_failed_login_invalid_password(self):
        """Test failed login with invalid password"""
        response = self.client.post(self.login_url, {
            'Email': 'testuser@example.com',
            'Password': 'wrongpassword'
        })
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Invalid password")
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 200)
    
    def test_login_with_empty_fields(self):
        """Test login attempt with empty fields"""
        # Test empty email
        response = self.client.post(self.login_url, {
            'Email': '',
            'Password': self.user_password
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Please provide both email and password")
        
        # Test empty password
        response = self.client.post(self.login_url, {
            'Email': 'testuser@example.com',
            'Password': ''
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Please provide both email and password")
    
    def test_email_case_sensitivity(self):
        """Test that email login is case insensitive"""
        # No need to create another user, use the one from setUp
        response = self.client.post(self.login_url, {
            'Email': 'TESTUSER@EXAMPLE.COM',  # Upper case email
            'Password': self.user_password
        })
        
        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(
            response.wsgi_request.user.email,
            'testuser@example.com'  # Verify stored as lowercase
        )
        
    def tearDown(self):
        """Clean up after each test"""
        CustomUser.objects.all().delete()  # Clean up users
        MediaFiles.objects.all().delete()  # Clean up media files
        Thumbnail.objects.all().delete()   # Clean up thumbnails

    def test_dashboard_view(self):
        """Test dashboard view displays users and videos"""
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/dashboard.html')
        self.assertIn('user', response.context)
        self.assertIn('video', response.context)

    def test_login_authenticated_redirect(self):
        """Test that authenticated users are redirected from login page"""
        self.client.force_login(self.user)  # Use force_login instead of login
        response = self.client.get(self.login_url, follow=True)  # Add follow=True to follow redirects
        self.assertRedirects(response, self.dashboard_url)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(self.login_url, {
            'Email': 'wrong@email.com',
            'Password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        """Test logout functionality"""
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, self.login_url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_register_valid_data(self):
        """Test registration with valid data"""
        response = self.client.post(self.register_url, {
            'fullname': 'New User',
            'Email': 'new@example.com',
            'Contact': '+254787654321',
            'Password': 'newpass123',
            'Password1': 'newpass123'
        })
        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(CustomUser.objects.filter(email='new@example.com').exists())

    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords"""
        response = self.client.post(self.register_url, {
            'fullname': 'New User',
            'Email': 'new@example.com', 
            'Contact': '+254787654321',
            'Password': 'pass123',
            'Password1': 'pass456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(email='new@example.com').exists())

    def test_upload_video(self):
        """Test video upload functionality"""
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.post(self.upload_video_url, {
            'title': 'Test Video',
            'video': self.video_file
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(MediaFiles.objects.filter(title='Test Video').exists())

    def test_upload_thumbnail(self):
        """Test thumbnail upload functionality"""
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.post(self.upload_thumbnail_url, {
            'images': self.image_file
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Thumbnail.objects.filter(cover__contains='test_image').exists())

    def test_register_duplicate_email(self):
        """Test registration with existing email"""
        # First create a user with the email we want to test
        CustomUser.objects.create_user(
            email='test@example.com',
            password='pass123',
            fullname='First User',
            phonenumber='+254700000002'
        )

        # Attempt to register with the same email
        response = self.client.post(self.register_url, {
            'fullname': 'Another User',
            'Email': 'test@example.com',  # Same email
            'Contact': '+254799999999',
            'Password': 'pass123',
            'Password1': 'pass123'
        }, follow=True)  # Follow redirect

        # Verify the second user was not created
        self.assertEqual(CustomUser.objects.filter(email='test@example.com').count(), 1)
        
        # Verify the new phone number wasn't registered
        self.assertFalse(CustomUser.objects.filter(phonenumber='+254799999999').exists())
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        error_message = 'Email already exists'
        self.assertTrue(
            any(error_message.lower() in str(msg).lower() for msg in messages),
            f"Expected message containing '{error_message}', got: {[str(m) for m in messages]}"
        )

    def test_register_duplicate_phone(self):
        """Test registration with existing phone number"""
        # First create a user with the phone number
        CustomUser.objects.create_user(
            email='first@example.com',
            password='pass123',
            fullname='First User',
            phonenumber='+254712345678'
        )

        # Attempt to register with the same phone number
        response = self.client.post(self.register_url, {
            'fullname': 'Another User',
            'Email': 'another@example.com',
            'Contact': '+254712345678',  # Same phone number
            'Password': 'pass123',
            'Password1': 'pass123'
        }, follow=True)  # Follow redirect

        # Verify the second user was not created
        self.assertFalse(CustomUser.objects.filter(email='another@example.com').exists())
        
        # Verify we have only one user with this phone number
        self.assertEqual(CustomUser.objects.filter(phonenumber='+254712345678').count(), 1)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        error_message = 'Phone number already exists'
        self.assertTrue(
            any(error_message.lower() in str(msg).lower() for msg in messages),
            f"Expected message containing '{error_message}', got: {[str(m) for m in messages]}"
        )

    def tearDown(self):
        # Clean up uploaded files
        MediaFiles.objects.all().delete()
        Thumbnail.objects.all().delete()