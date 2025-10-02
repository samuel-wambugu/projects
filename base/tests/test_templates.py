from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from base.models import Tutorial, Subscription, CurrencyPair, UserProgress
from datetime import timedelta

class TemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
            fullname='Test User',
            phonenumber='+254700000001'
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            fullname='Admin User',
            phonenumber='+254700000002'
        )
        
        # Create test tutorial
        self.tutorial = Tutorial.objects.create(
            title='Test Tutorial',
            content='Test Content',
            level='beginner',
            order=1,
            free_access=True,
            is_featured=True
        )
        
        # Create test subscription
        self.subscription = Subscription.objects.create(
            user=self.user,
            subscription_type='monthly',
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=999
        )
        
        # Create test currency pair
        self.currency_pair = CurrencyPair.objects.create(
            base_currency='EUR',
            quote_currency='USD',
            current_rate=1.0500,
            daily_high=1.0600,
            daily_low=1.0400,
            daily_change=0.25
        )
        
        # Create user progress
        self.user_progress = UserProgress.objects.create(
            user=self.user,
            tutorial=self.tutorial,
            completed=True
        )

    def test_home_template(self):
        """Test home page template for anonymous and authenticated users"""
        # Test for anonymous user
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')
        self.assertContains(response, 'Get Started')
        
        # Test for authenticated user (should redirect to dashboard)
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_dashboard_template(self):
        """Test dashboard template and context"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/dashboard.html')
        
        # Check context
        self.assertIn('subscription', response.context)
        self.assertIn('tutorials', response.context)
        self.assertIn('currency_pairs', response.context)
        self.assertIn('progress_percentage', response.context)
        
        # Check content
        self.assertContains(response, 'Welcome back, Test User!')
        self.assertContains(response, 'Premium member')
        self.assertContains(response, 'Test Tutorial')
        self.assertContains(response, 'EUR/USD')

    def test_subscription_template(self):
        """Test subscription plans template"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('subscription_plans'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/subscription_plans.html')
        
        # Check content
        self.assertContains(response, 'Monthly')
        self.assertContains(response, 'Quarterly')
        self.assertContains(response, 'Yearly')
        self.assertContains(response, 'Ksh')  # Check currency symbol

    def test_admin_dashboard_elements(self):
        """Test admin-specific elements in dashboard template"""
        # Test as regular user (should not see admin controls)
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertNotContains(response, 'Upload Tutorial Video')
        
        # Test as admin user (should see admin controls)
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'Upload Tutorial Video')
        self.assertContains(response, 'Admin Controls')

    def test_navbar_template(self):
        """Test navbar template content"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        # Check navbar content
        self.assertContains(response, 'Forex Academy')
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Tutorials')
        self.assertContains(response, 'Forex')
        self.assertContains(response, 'Plans')
        self.assertContains(response, 'Test User')  # User's name in navbar
        
        # Check logout link
        self.assertContains(response, 'Logout')

    def test_template_inheritance(self):
        """Test proper template inheritance and static files"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        # Check base template elements
        self.assertContains(response, 'bootstrap.min.css')
        self.assertContains(response, 'font-awesome')
        self.assertContains(response, 'style.css')
        self.assertContains(response, 'bootstrap.bundle.min.js')
        
        # Check footer content
        self.assertContains(response, 'Forex Trading Academy')
        self.assertContains(response, 'All rights reserved')
        self.assertContains(response, 'Quick Links')