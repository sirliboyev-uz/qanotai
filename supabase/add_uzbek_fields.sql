-- Add Uzbek localization fields to subscription_plans table
ALTER TABLE subscription_plans
ADD COLUMN IF NOT EXISTS price_uzs INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS display_name_uz TEXT,
ADD COLUMN IF NOT EXISTS description_uz TEXT;

-- Update existing plans with UZS prices and Uzbek translations
UPDATE subscription_plans SET
    price_uzs = 0,
    display_name_uz = 'Bepul',
    description_uz = 'Oyiga 3 ta bepul test'
WHERE name = 'free';

UPDATE subscription_plans SET
    price_uzs = 29000,
    display_name_uz = 'Oddiy',
    description_uz = 'Boshlovchilar uchun - oyiga 50 ta test'
WHERE name = 'basic';

UPDATE subscription_plans SET
    price_uzs = 49000,
    display_name_uz = 'Standart',
    description_uz = 'Eng mashhur - oyiga 200 ta test'
WHERE name = 'standard';

UPDATE subscription_plans SET
    price_uzs = 79000,
    display_name_uz = 'Premium',
    description_uz = 'Cheksiz testlar va barcha imkoniyatlar'
WHERE name = 'premium';

UPDATE subscription_plans SET
    price_uzs = 990000,
    display_name_uz = 'Umrbod',
    description_uz = 'Bir martalik to''lov, abadiy cheksiz'
WHERE name = 'lifetime';

-- Add order_id and transaction_id to payments table for Payme integration
ALTER TABLE payments
ADD COLUMN IF NOT EXISTS order_id TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS transaction_id TEXT,
ADD COLUMN IF NOT EXISTS payment_method TEXT DEFAULT 'payme',
ADD COLUMN IF NOT EXISTS amount_uzs INTEGER,
ADD COLUMN IF NOT EXISTS amount_tiyin BIGINT,
ADD COLUMN IF NOT EXISTS subscription_plan TEXT,
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;

-- Create index for faster payment lookups
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);

-- Add Uzbek language fields to other tables
ALTER TABLE question_topics
ADD COLUMN IF NOT EXISTS name_uz TEXT,
ADD COLUMN IF NOT EXISTS description_uz TEXT;

ALTER TABLE questions
ADD COLUMN IF NOT EXISTS text_uz TEXT,
ADD COLUMN IF NOT EXISTS sample_answer_uz TEXT,
ADD COLUMN IF NOT EXISTS tips_uz TEXT;

ALTER TABLE daily_challenges
ADD COLUMN IF NOT EXISTS title_uz TEXT,
ADD COLUMN IF NOT EXISTS description_uz TEXT,
ADD COLUMN IF NOT EXISTS theme_uz TEXT;

ALTER TABLE achievements
ADD COLUMN IF NOT EXISTS name_uz TEXT,
ADD COLUMN IF NOT EXISTS description_uz TEXT;

-- Update some sample Uzbek translations for topics
UPDATE question_topics SET
    name_uz = 'Texnologiya va zamonaviy hayot',
    description_uz = 'Texnologiyaning jamiyatga ta''siri, ijtimoiy tarmoqlar va raqamli transformatsiya'
WHERE name = 'Technology and Modern Life';

UPDATE question_topics SET
    name_uz = 'Atrof-muhit muammolari',
    description_uz = 'Iqlim o''zgarishi, barqarorlik va atrof-muhitni muhofaza qilish'
WHERE name = 'Environmental Issues';

UPDATE question_topics SET
    name_uz = 'Ta''lim tizimlari',
    description_uz = 'Ta''lim tizimlarini taqqoslash, onlayn ta''lim va ta''lim texnologiyalari'
WHERE name = 'Education Systems';

UPDATE question_topics SET
    name_uz = 'Sog''liqni saqlash va turmush tarzi',
    description_uz = 'Jismoniy va ruhiy salomatlik, fitnes, dieta va farovonlik'
WHERE name = 'Health and Lifestyle';

UPDATE question_topics SET
    name_uz = 'Ish va karyera',
    description_uz = 'Bandlik, karyera rivojlanishi, ish-hayot balansi'
WHERE name = 'Work and Career';

-- Add comment to document the UZS currency
COMMENT ON COLUMN subscription_plans.price_uzs IS 'Price in Uzbek Som (UZS)';
COMMENT ON COLUMN payments.amount_uzs IS 'Payment amount in Uzbek Som';
COMMENT ON COLUMN payments.amount_tiyin IS 'Payment amount in tiyin (1 UZS = 100 tiyin)';

-- Grant necessary permissions
GRANT SELECT ON subscription_plans TO anon;
GRANT SELECT ON payments TO authenticated;
GRANT INSERT, UPDATE ON payments TO authenticated;