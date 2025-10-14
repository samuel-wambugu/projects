# M-PESA INTEGRATION SETUP GUIDE

## 🎯 Overview
Your website is now ready for M-Pesa payments! This guide shows you how to switch from sandbox (testing) to production (real money) when you get your PayBill.

---

## 📋 Current Status

✅ **What's Already Done:**
- M-Pesa integration with django_daraja installed
- Payment forms on subscription page
- STK Push implementation
- Callback handlers for payment confirmation
- Proper error handling
- Session management for payments
- Subscription activation logic

⏳ **What You Need:**
- PayBill number from Safaricom
- API credentials from Safaricom Developer Portal

---

## 🚀 Quick Start (Testing Mode)

Your site is currently in **SANDBOX MODE** - perfect for testing without real money.

### Test Phone Numbers (Sandbox Only):
- `254708374149`
- `254711111111`

### Test the Payment Flow:
1. Start your Django server
2. Go to `/subscriptions/`
3. Click "Subscribe Now" on any plan
4. Enter test phone: `254708374149`
5. You'll see a success message (no real payment needed)

---

## 💼 Getting Your PayBill (Production Setup)

### Step 1: Register Your Business
1. Register business with county government
2. Get business certificate
3. Apply for KRA PIN
4. Open business bank account

**Cost:** ~KSh 10,000 - 15,000

### Step 2: Apply for PayBill
1. Visit Safaricom shop with:
   - Business registration certificate
   - KRA PIN certificate
   - ID/Passport
   - Bank account details

2. Or call Safaricom Business: **0711 234 567**

3. Or apply online: https://www.safaricom.co.ke/paybill

**Cost:** ~KSh 3,000 setup fee
**Time:** 1-2 weeks approval

### Step 3: Get API Access
1. Go to https://developer.safaricom.co.ke/
2. Create account
3. Create new production app
4. Copy your credentials:
   - Consumer Key
   - Consumer Secret
5. Contact Safaricom to get your PassKey

---

## ⚙️ Switching to Production

### When You Receive Your PayBill:

#### 1. Update `Trading/settings.py`:

```python
# CHANGE THIS LINE:
MPESA_ENVIRONMENT = 'sandbox'
# TO:
MPESA_ENVIRONMENT = 'production'

# UPDATE THESE WITH YOUR ACTUAL CREDENTIALS:
MPESA_CONSUMER_KEY = 'YOUR_PRODUCTION_KEY_HERE'  # From developer portal
MPESA_CONSUMER_SECRET = 'YOUR_PRODUCTION_SECRET_HERE'  # From developer portal
MPESA_SHORTCODE = 'YOUR_PAYBILL_NUMBER'  # e.g., '123456'
MPESA_EXPRESS_SHORTCODE = 'YOUR_PAYBILL_NUMBER'  # Same as above
MPESA_PASSKEY = 'YOUR_PRODUCTION_PASSKEY'  # From Safaricom

# UPDATE YOUR DOMAIN (IMPORTANT!):
MPESA_CALLBACK_URL = 'https://yourdomain.com/mpesa/callback/'
MPESA_TIMEOUT_URL = 'https://yourdomain.com/mpesa/timeout/'
```

#### 2. Deploy Your Website with HTTPS:
M-Pesa requires HTTPS for callbacks. Options:
- **Recommended:** Use PythonAnywhere, Heroku, or DigitalOcean
- Get free SSL with Let's Encrypt
- Or use Cloudflare for SSL

#### 3. Test with Small Amounts First:
- Create a KSh 1 test plan
- Try payment with your own M-Pesa
- Verify money arrives in your PayBill
- Verify subscription activates correctly

#### 4. Go Live:
- Set your real subscription prices
- Announce to customers
- Monitor payments in Django admin

---

## 🧪 Testing Locally (Before Production)

### Use Ngrok for Local Testing:

```bash
# 1. Download ngrok from https://ngrok.com/download

# 2. Start your Django server
cd /home/samuel/Desktop/brayowebsite/Trading
source ../brayo/bin/activate
python manage.py runserver

# 3. In another terminal, start ngrok
ngrok http 8000

# 4. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

# 5. Update settings.py temporarily:
MPESA_CALLBACK_URL = 'https://abc123.ngrok.io/mpesa/callback/'
MPESA_TIMEOUT_URL = 'https://abc123.ngrok.io/mpesa/timeout/'

# 6. Test payments with sandbox credentials
```

---

## 💰 How Money Reaches You

### Money Flow:
```
Customer pays KSh 999
      ↓
Your PayBill (123456)
      ↓
Business M-Pesa Account
      ↓
You withdraw to:
  • Bank account (daily auto-settlement)
  • Personal M-Pesa (manually via Till)
  • Keep for business use
```

### Withdrawal Options:

1. **Auto-Settlement to Bank:**
   - Configure with Safaricom
   - Money auto-transferred to bank daily
   - Most convenient for large volumes

2. **Manual Withdrawal:**
   - Log into M-Pesa Business Portal
   - Withdraw to bank or personal M-Pesa
   - You control timing

3. **Via Till:**
   - Use business M-Pesa app
   - Transfer to personal number
   - Instant

---

## 💵 Fees & Costs

### Safaricom Charges:
- **Transaction Fee:** 0.5% - 1.5% per transaction
- **Monthly Fee:** KSh 500 - 1,000
- **Withdrawal Fee:** Standard M-Pesa rates

### Example (50 customers at KSh 999 each):
```
Total Revenue: KSh 49,950
Transaction Fees (1%): -KSh 500
Monthly Fee: -KSh 1,000
─────────────────────────────
Net Profit: KSh 48,450
```

---

## 🔍 Monitoring Payments

### Check Payment Status:

```bash
# Start Django shell
cd /home/samuel/Desktop/brayowebsite/Trading
source ../brayo/bin/activate
python manage.py shell

# Check active subscriptions
>>> from base.models import Subscription
>>> Subscription.objects.filter(is_active=True).count()

# Check recent payments
>>> Subscription.objects.order_by('-created_at')[:5]
```

### Via Django Admin:
1. Go to `/admin/`
2. Login as superuser
3. Click "Subscriptions"
4. View all payments and statuses

---

## 🚨 Troubleshooting

### "Payment system unavailable"
- Check `MPESA_CONSUMER_KEY` is set correctly
- Verify django_daraja is installed: `pip list | grep daraja`

### "Payment initiated but not received"
- Check callback URL is accessible (must be HTTPS)
- Check Django logs: `python manage.py runserver` (look for errors)
- Verify CheckoutRequestID matches between request and callback

### "Payment successful but subscription not activated"
- Check Django logs for errors in callback handler
- Verify Subscription model has all required fields
- Check if callback reached your server (use ngrok for local testing)

### Customer says "Prompt didn't arrive"
- Verify phone number format: `254XXXXXXXXX` (no +, spaces, or 0)
- Check if customer's M-Pesa is active
- Try with different phone number

---

## 📞 Support Contacts

### Safaricom Support:
- Business Line: **0711 234 567**
- Developer Support: https://developer.safaricom.co.ke/support
- M-Pesa Support: **234** (from Safaricom line)

### Developer Resources:
- API Docs: https://developer.safaricom.co.ke/docs
- Sandbox Testing: https://developer.safaricom.co.ke/test-credentials
- Community Forum: https://developer.safaricom.co.ke/community

---

## ✅ Pre-Launch Checklist

Before going live with real money:

- [ ] PayBill received from Safaricom
- [ ] Production API credentials obtained
- [ ] Website deployed with HTTPS
- [ ] `MPESA_ENVIRONMENT = 'production'` in settings
- [ ] `MPESA_CONSUMER_KEY` updated with production key
- [ ] `MPESA_CONSUMER_SECRET` updated with production secret
- [ ] `MPESA_SHORTCODE` updated with YOUR PayBill
- [ ] `MPESA_PASSKEY` updated with production passkey
- [ ] `MPESA_CALLBACK_URL` updated with live domain
- [ ] Tested payment with KSh 1 successfully
- [ ] Money received in PayBill account
- [ ] Subscription activated correctly
- [ ] Django admin accessible for monitoring
- [ ] Backup and error logging configured

---

## 🎉 You're Ready!

Your M-Pesa integration is properly set up. When you get your PayBill:

1. Update the 5 settings in `settings.py`
2. Deploy with HTTPS
3. Test with small amount
4. Go live!

**Questions?** Check the troubleshooting section or contact Safaricom support.

---

**Last Updated:** October 14, 2025
**Django Version:** 5.2.6
**django_daraja Version:** 1.3.0
