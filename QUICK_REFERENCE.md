# 🚀 QUICK REFERENCE - M-PESA SETUP

## When You Get Your PayBill, Update These 5 Settings:

### File: `/home/samuel/Desktop/brayowebsite/Trading/Trading/settings.py`

```python
# LINE ~160 - Change these 5 values:

# 1. Environment
MPESA_ENVIRONMENT = 'production'  # Change from 'sandbox' to 'production'

# 2. Consumer Key (from developer.safaricom.co.ke)
MPESA_CONSUMER_KEY = 'YOUR_KEY_HERE'  # Replace 'your_consumer_key_here'

# 3. Consumer Secret (from developer.safaricom.co.ke)
MPESA_CONSUMER_SECRET = 'YOUR_SECRET_HERE'  # Replace 'your_consumer_secret_here'

# 4. Your PayBill Number (from Safaricom Business)
MPESA_SHORTCODE = '123456'  # Replace '174379' with YOUR PayBill

# 5. Production PassKey (from Safaricom)
MPESA_PASSKEY = 'YOUR_PASSKEY_HERE'  # Replace the long test passkey

# 6. Your Website URL (MUST be HTTPS)
MPESA_CALLBACK_URL = 'https://yourdomain.com/mpesa/callback/'  # Replace yourdomain.com
```

---

## 📁 Files to Check Before Going Live:

### 1. Settings File:
```
/Trading/Trading/settings.py
Lines: 160-190 (M-Pesa Configuration Section)
```

### 2. Views File (Payment Logic):
```
/Trading/base/views.py
Lines: 314-430 (initiate_payment, mpesa_callback, mpesa_timeout)
✅ Already properly configured - no changes needed
```

### 3. URLs File (Payment Routes):
```
/Trading/base/urls.py
Lines: 28-30 (M-Pesa URLs)
✅ Already configured correctly
```

### 4. Template (Payment Form):
```
/Trading/base/templates/base/subscription_plans.html
✅ Already set up with proper forms
```

---

## 🧪 Testing Checklist:

### Sandbox Testing (No PayBill Needed):
```bash
# 1. Start server
cd /home/samuel/Desktop/brayowebsite/Trading
source ../brayo/bin/activate
python manage.py runserver

# 2. Test payment
# - Go to: http://localhost:8000/subscriptions/
# - Use phone: 254708374149
# - Submit payment
# - Should see success message
```

### Production Testing (After Getting PayBill):
```bash
# 1. Update 5 settings in settings.py (see above)

# 2. Deploy with HTTPS (required!)

# 3. Test with YOUR phone number:
# - Go to: https://yourdomain.com/subscriptions/
# - Use YOUR number: 254XXXXXXXXX
# - You'll receive STK push on your phone
# - Enter M-Pesa PIN
# - Money goes to YOUR PayBill!

# 4. Verify:
# - Check M-Pesa message for confirmation
# - Check Django admin: /admin/
# - Check subscription activated
```

---

## 💡 Common Issues & Quick Fixes:

### Issue: "Payment system unavailable"
**Fix:** Check MPESA_CONSUMER_KEY is not 'your_consumer_key_here'
```bash
# Run this to check:
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MPESA_CONSUMER_KEY)
# Should show actual key, not 'your_consumer_key_here'
```

### Issue: "STK push didn't arrive"
**Fix:** Phone number format
```
❌ Wrong: +254712345678, 0712345678
✅ Correct: 254712345678
```

### Issue: "Payment successful but no subscription"
**Fix:** Callback URL not reachable
```python
# Must be HTTPS and publicly accessible
# Use ngrok for local testing:
# ngrok http 8000
# Then update MPESA_CALLBACK_URL with ngrok URL
```

---

## 📱 Test Phone Numbers (Sandbox Only):

- `254708374149` - Standard test
- `254711111111` - Alternative test

**Note:** These only work in SANDBOX mode!

---

## 💰 Where Does Money Go?

```
Customer → PayBill (YOUR_NUMBER) → Business M-Pesa Account

Withdraw to:
  ├─ Bank account (auto-settlement)
  ├─ Personal M-Pesa (manual transfer)
  └─ Keep in business account
```

---

## 🔐 Security Notes:

1. **Never commit credentials to Git:**
```bash
# Add to .gitignore:
*.env
settings_local.py
```

2. **Use environment variables in production:**
```python
import os
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')
```

3. **Enable HTTPS before going live**

---

## 📊 Monitor Payments:

### Via Django Shell:
```bash
python manage.py shell

>>> from base.models import Subscription
>>> Subscription.objects.filter(is_active=True).count()  # Active subs
>>> Subscription.objects.order_by('-created_at').first()  # Latest payment
```

### Via Django Admin:
```
Go to: /admin/
Login with superuser
Click: Subscriptions
View all payments and dates
```

---

## 🎯 Go-Live Steps (In Order):

1. ✅ **Code is ready** (already done!)
2. ⏳ **Get PayBill** (1-2 weeks from Safaricom)
3. ⏳ **Get API credentials** (developer.safaricom.co.ke)
4. ⏳ **Deploy website with HTTPS**
5. ⏳ **Update 5 settings** (see top of this file)
6. ⏳ **Test with KSh 1**
7. ⏳ **Verify money received**
8. ⏳ **Go live!**

---

## 📞 Quick Contacts:

- **Safaricom Business:** 0711 234 567
- **M-Pesa Support:** Dial 234 (Safaricom line)
- **Developer Portal:** developer.safaricom.co.ke
- **Apply PayBill:** safaricom.co.ke/paybill

---

## ✅ What's Already Working:

✅ M-Pesa integration installed (django_daraja)
✅ Payment forms on /subscriptions/
✅ STK Push implementation
✅ Callback handler for confirmations
✅ Error handling
✅ Subscription activation logic
✅ User notifications
✅ Session management
✅ Phone number validation
✅ Amount handling
✅ CSS files error-free
✅ URL routing configured
✅ Templates properly set up

---

## 🎉 You're 90% Done!

**Just need:**
1. PayBill number from Safaricom
2. API credentials from developer portal
3. Update 5 lines in settings.py
4. Deploy with HTTPS
5. Test and go live!

**Everything else is already set up and working!**

---

**File Location:** /home/samuel/Desktop/brayowebsite/Trading/QUICK_REFERENCE.md
**Last Updated:** October 14, 2025
