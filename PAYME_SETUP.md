# 💳 Payme Integration Setup for QanotAI

## 🇺🇿 O'zbek foydalanuvchilar uchun to'lov tizimi

QanotAI ilovasi O'zbekiston bozoriga mo'ljallangan bo'lib, Payme to'lov tizimi orqali ishlaydi.

## 📋 Payme Merchant Registration

### Step 1: Register as Merchant

1. Go to [Payme Business](https://business.payme.uz)
2. Register your business account
3. Submit required documents:
   - Business registration certificate (Guvohnoma)
   - Bank account details
   - Tax ID (INN)
   - Contact information

### Step 2: Get API Credentials

After approval, you'll receive:
- **Merchant ID**: Your unique merchant identifier
- **Secret Key**: For signature verification
- **Test Credentials**: For development/testing

### Step 3: Configure Webhook URL

In Payme Business Cabinet:
1. Go to **Settings** → **API Settings**
2. Set Webhook URL: `https://your-domain.com/api/payment/payme-webhook`
3. Enable test mode for development

## 🔧 Backend Configuration

### Update .env file:

```env
# Payme Payment Configuration
PAYME_MERCHANT_ID=your-merchant-id-here
PAYME_SECRET_KEY=your-secret-key-here
PAYME_TEST_MODE=true  # Set to false for production
```

## 💰 Subscription Pricing (UZS)

Our subscription plans for Uzbek market:

| Plan | Price (UZS) | Features |
|------|------------|----------|
| **Basic** | 29,000/month | 50 tests/month |
| **Standard** | 49,000/month | 200 tests/month |
| **Premium** | 79,000/month | Unlimited tests |
| **Lifetime** | 990,000 | One-time payment, unlimited forever |

## 🔄 Payment Flow

### 1. User Initiates Payment

```dart
// Flutter app code
final response = await http.post(
  '/api/payment/create-payment',
  body: {
    'subscription_plan': 'standard'
  }
);

// Response contains payment URL
final paymentUrl = response['payment_url'];
// Open in WebView or external browser
```

### 2. Payme Webhook Processing

The backend automatically handles Payme callbacks:

- `CheckPerformTransaction` - Validates if payment can be made
- `CreateTransaction` - Creates transaction record
- `PerformTransaction` - Completes payment & activates subscription
- `CancelTransaction` - Handles cancellations
- `CheckTransaction` - Status checks
- `GetStatement` - Transaction history

### 3. Subscription Activation

After successful payment:
1. Payment marked as completed
2. User subscription activated
3. Usage limits updated
4. User can access premium features

## 🧪 Testing

### Test Cards (Payme Test Mode)

Use these test cards in test mode:
- **Success**: 8600 0691 9540 6311
- **Insufficient Funds**: 8600 3434 1734 2639
- **Card Expired**: 8600 0609 0917 5727

### Test Payment Flow

```bash
# 1. Create payment link
curl -X POST http://localhost:8000/api/payment/create-payment \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"subscription_plan": "basic"}'

# 2. Check payment status
curl http://localhost:8000/api/payment/check-payment/ORDER_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📱 Mobile App Integration

### iOS Deep Link Setup

In `Info.plist`:
```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>qanotai</string>
        </array>
    </dict>
</array>
```

### Android Deep Link Setup

In `AndroidManifest.xml`:
```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="qanotai" />
</intent-filter>
```

### Flutter WebView Implementation

```dart
import 'package:webview_flutter/webview_flutter.dart';

class PaymePaymentScreen extends StatefulWidget {
  final String paymentUrl;
  
  @override
  Widget build(BuildContext context) {
    return WebView(
      initialUrl: paymentUrl,
      javascriptMode: JavascriptMode.unrestricted,
      navigationDelegate: (NavigationRequest request) {
        if (request.url.startsWith('qanotai://')) {
          // Handle deep link
          if (request.url.contains('payment-success')) {
            Navigator.pop(context, true);
          }
          return NavigationDecision.prevent;
        }
        return NavigationDecision.navigate;
      },
    );
  }
}
```

## 🚀 Production Checklist

- [ ] Get production Merchant ID from Payme
- [ ] Update PAYME_TEST_MODE to false
- [ ] Configure production webhook URL
- [ ] Set up SSL certificate (HTTPS required)
- [ ] Test with real payment cards
- [ ] Monitor webhook logs
- [ ] Set up payment notifications

## 📊 Payment Analytics

Track these metrics:
- Conversion rate (visits to payments)
- Payment success rate
- Popular subscription plans
- Churn rate
- Average revenue per user (ARPU)

## 🔒 Security Notes

1. **Never expose Secret Key** in client code
2. **Always verify webhook signatures**
3. **Use HTTPS for production**
4. **Log all payment transactions**
5. **Implement rate limiting** on payment endpoints
6. **Store sensitive data encrypted**

## 📞 Payme Support

- Business Support: +998 78 777 47 47
- Email: support@payme.uz
- Documentation: [developer.payme.uz](https://developer.payme.uz)
- Business Cabinet: [business.payme.uz](https://business.payme.uz)

## 🎯 Next Steps

1. Complete merchant registration
2. Get API credentials
3. Test payment flow in test mode
4. Submit app for Payme review
5. Go live with production credentials

---

**Note**: This integration is specifically designed for the Uzbek market. For international expansion, consider adding Stripe or PayPal alongside Payme.