from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import CustomUser, Tutorial, Comments, Subscription
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.conf import settings
from django.utils import timezone
import tempfile
import shutil
import json
from datetime import timedelta

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ViewsTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        # Clean up temporary test media files
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

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

        # Create a valid image file for testing
        import tempfile
        from PIL import Image
        
        # Create a temporary image file
        image = Image.new('RGB', (100, 100), 'white')
        self.thumbnail_temp = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.thumbnail_temp.name, 'JPEG')
        
        # Create test image file
        self.image_file = SimpleUploadedFile(
            "test_image.jpg",
            open(self.thumbnail_temp.name, 'rb').read(),
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
        self.assertRedirects(response, reverse('dashboard'))
        
    def test_subscription_plans_view(self):
        """Test subscription plans page display"""
        # Test without login should redirect
        self.client.logout()
        response = self.client.get(reverse('subscription_plans'))
        self.assertEqual(response.status_code, 302)
        
        # Test with login should show plans
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.get(reverse('subscription_plans'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/subscription_plans.html')
        
    def test_initiate_payment_view(self):
        """Test initiating M-Pesa payment"""
        # Test without login should redirect
        self.client.logout()
        response = self.client.post(reverse('initiate_payment'))
        self.assertEqual(response.status_code, 302)
        
        # Test with login but missing data
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.post(reverse('initiate_payment'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Please provide all required information' in str(m) for m in messages))
        
        # Test with valid data
        response = self.client.post(reverse('initiate_payment'), {
            'phone_number': '254712345678',
            'amount': '999',
            'subscription_type': 'monthly'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect back to plans page
        
    @override_settings(MPESA_ENVIRONMENT='sandbox')
    def test_mpesa_callback(self):
        """Test M-Pesa callback processing"""
        # Setup test data
        checkout_request_id = 'ws_CO_123456789'
        self.client.login(email=self.user.email, password=self.user_password)
        session = self.client.session
        session['pending_payment'] = {
            'checkout_request_id': checkout_request_id,
            'subscription_type': 'monthly',
            'amount': '999'
        }
        session.save()
        
        # Test successful payment callback
        callback_data = {
            'Body': {
                'stkCallback': {
                    'ResultCode': 0,
                    'CheckoutRequestID': checkout_request_id
                }
            }
        }
        response = self.client.post(
            reverse('mpesa_callback'),
            data=json.dumps(callback_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        # Verify subscription was created
        subscription = Subscription.objects.filter(user=self.user, subscription_type='monthly').first()
        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.payment_reference, checkout_request_id)
        self.assertTrue(subscription.end_date > timezone.now())
        
        # Test invalid callback data
        response = self.client.post(
            reverse('mpesa_callback'),
            data=json.dumps({'invalid': 'data'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)  # Bad request for invalid data structure
        self.assertEqual(response.json()['status'], 'error')
        self.assertEqual(response.json()['message'], 'Missing required fields')
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
        Tutorial.objects.all().delete()  # Clean up tutorials
        Comments.objects.all().delete()  # Clean up comments

    def test_dashboard_view(self):
        """Test dashboard view displays users and videos"""
        # Login using the correct credentials
        self.client.login(email='testuser@example.com', password=self.user_password)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/dashboard.html')
        self.assertIn('user', response.context)

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
        upload_url = reverse('upload_video')
        
        # Test without login
        response = self.client.get(upload_url)
        self.assertRedirects(response, f"{reverse('login')}?next={upload_url}")
        
        # Test with regular user
        user = CustomUser.objects.create_user(
            email='user@example.com',
            password='userpass123',
            fullname='Regular User',
            phonenumber='+254700000088'
        )
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(upload_url)
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        
        # Create and login as superuser
        superuser = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            fullname='Admin User',
            phonenumber='+254700000099'
        )
        self.client.login(email='admin@example.com', password='adminpass123')
        
        # Create test video and thumbnail files
        video_file = SimpleUploadedFile(
            name='test_video.mp4',
            content=b'file_content',
            content_type='video/mp4'
        )
        
        thumbnail_file = SimpleUploadedFile(
            name='test_thumb.jpg',
            content=b'file_content',
            content_type='image/jpeg'
        )
        
        # Upload the video and thumbnail
        data = {
            'title': 'Test Video',
            'video': video_file,
            'thumbnail': thumbnail_file
        }
        response = self.client.post(self.upload_video_url, data)
        
        # Check response and database
        self.assertEqual(response.status_code, 200, 
                        f"Response status: {response.status_code}, "
                        f"Content: {response.content.decode()}")
        
        # Verify tutorial was created
        self.assertTrue(
            Tutorial.objects.filter(title='Test Video').exists(),
            "Tutorial was not created in database"
        )

    def test_upload_thumbnail(self):
        """Test thumbnail upload functionality"""
        self.client.login(email=self.user.email, password=self.user_password)
        
        # First create a tutorial
        tutorial = Tutorial.objects.create(
            title='Test Tutorial',
            content='Test content',
            order=1,
            author=self.user
        )
        
        # Now add a thumbnail to it
        response = self.client.post(self.upload_thumbnail_url, {
            'thumbnail': self.image_file,
            'tutorial_id': tutorial.id
        })
        
        # Refresh tutorial from database
        tutorial.refresh_from_db()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(tutorial.thumbnail.name.endswith('test_image.jpg'))

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

    def test_admin_dashboard_access(self):
        """Test that only superusers can access admin dashboard"""
        admin_dashboard_url = reverse('admin_dashboard')
        
        # Test access without login
        response = self.client.get(admin_dashboard_url)
        self.assertRedirects(response, f"{reverse('login')}?next={admin_dashboard_url}")
        
        # Test access with regular user
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.get(admin_dashboard_url)
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        
        # Create and test with superuser
        superuser = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            fullname='Admin User',
            phonenumber='+254700000099'
        )
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/admin_dashboard.html')

    def test_create_tutorial_access(self):
        """Test that only superusers can create tutorials"""
        create_tutorial_url = reverse('create_tutorial')
        
        # Test access without login
        response = self.client.get(create_tutorial_url)
        self.assertRedirects(response, f"{reverse('login')}?next={create_tutorial_url}")
        
        # Test access with regular user
        user = CustomUser.objects.create_user(
            email='user@example.com',
            password='userpass123',
            fullname='Regular User',
            phonenumber='+254700000088'
        )
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(create_tutorial_url)
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        
        # Test with superuser
        superuser = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            fullname='Admin User',
            phonenumber='+254700000099'
        )
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(create_tutorial_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/tutorial_form.html')

    def test_create_tutorial_with_price(self):
        """Test creating a tutorial with price"""
        create_tutorial_url = reverse('create_tutorial')
        
        superuser = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            fullname='Admin User',
            phonenumber='+254700000099')
            
        self.client.login(email='admin@example.com', password='adminpass123')
        
        # Create a valid image file
        import tempfile
        from PIL import Image
        
        # Create a temporary image file
        image = Image.new('RGB', (100, 100), 'white')
        thumbnail_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(thumbnail_file.name, 'JPEG')
        
        # Prepare tutorial data with file uploads
        data = {
            'title': 'Paid Tutorial',
            'content': 'This is a paid tutorial',
            'price': '99.99',
            'order': 1,
            'level': 'beginner',  # Added required field
            'video': SimpleUploadedFile(
                "test_video.mp4",
                b"file_content",
                content_type="video/mp4"
            ),
            'thumbnail': SimpleUploadedFile(
                "test_image.jpg",
                open(thumbnail_file.name, 'rb').read(),
                content_type="image/jpeg"
            )
        }
        
        # Submit the tutorial
        response = self.client.post(create_tutorial_url, data)
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # Verify tutorial was created with correct price and author
        tutorial = Tutorial.objects.get(title='Paid Tutorial')
        self.assertEqual(float(tutorial.price), 99.99)
        self.assertEqual(tutorial.author, superuser)
        self.assertTrue(tutorial.video)
        self.assertTrue(tutorial.thumbnail)

    def tearDown(self):
        # Clean up uploaded files
        Tutorial.objects.all().delete()
        Comments.objects.all().delete()