-- QanotAI Supabase Database Schema
-- IELTS Speaking Test Platform

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- USERS & AUTHENTICATION
-- =====================================================

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    phone_number TEXT UNIQUE,
    email TEXT UNIQUE,
    display_name TEXT,
    photo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- User profiles for additional information
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    bio TEXT,
    country TEXT,
    language_preferences TEXT[] DEFAULT ARRAY['en'],
    timezone TEXT DEFAULT 'UTC',
    ielts_target_score DECIMAL(2,1),
    test_date DATE,
    preparation_level TEXT CHECK (preparation_level IN ('beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- =====================================================
-- SUBSCRIPTIONS & PAYMENTS
-- =====================================================

-- Subscription plans
CREATE TABLE IF NOT EXISTS public.subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    tier TEXT NOT NULL CHECK (tier IN ('free', 'basic', 'premium', 'professional')),
    price_usd DECIMAL(10,2) NOT NULL,
    billing_period_months INTEGER NOT NULL,
    monthly_test_limit INTEGER,
    features JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User subscriptions
CREATE TABLE IF NOT EXISTS public.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES public.subscription_plans(id),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'paused')),
    start_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_date TIMESTAMPTZ,
    next_billing_date TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT false,
    payment_method_id TEXT,
    stripe_subscription_id TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payment records
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES public.user_subscriptions(id),
    amount_usd DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    payment_method TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    stripe_payment_intent_id TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage quotas
CREATE TABLE IF NOT EXISTS public.usage_quotas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    tests_used INTEGER DEFAULT 0,
    tests_limit INTEGER DEFAULT 3,
    bonus_tests INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, period_start)
);

-- =====================================================
-- CONTENT & QUESTIONS
-- =====================================================

-- Question topics
CREATE TABLE IF NOT EXISTS public.question_topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    difficulty_level TEXT CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    tags TEXT[] DEFAULT '{}',
    keywords TEXT[] DEFAULT '{}',
    popularity_score DECIMAL(3,2) DEFAULT 0,
    is_trending BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Questions bank
CREATE TABLE IF NOT EXISTS public.questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID REFERENCES public.question_topics(id),
    part INTEGER NOT NULL CHECK (part IN (1, 2, 3)),
    text TEXT NOT NULL,
    difficulty TEXT CHECK (difficulty IN ('easy', 'medium', 'hard')),
    category TEXT,
    tags TEXT[] DEFAULT '{}',
    keywords TEXT[] DEFAULT '{}',
    sample_answer TEXT,
    tips TEXT,
    estimated_time_seconds INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily challenges
CREATE TABLE IF NOT EXISTS public.daily_challenges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    challenge_date DATE NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    theme TEXT,
    part_1_questions UUID[] DEFAULT '{}',
    part_2_question UUID,
    part_3_questions UUID[] DEFAULT '{}',
    focus_skills TEXT[] DEFAULT '{}',
    estimated_duration_minutes INTEGER DEFAULT 15,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User challenge participation
CREATE TABLE IF NOT EXISTS public.user_challenges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    challenge_id UUID NOT NULL REFERENCES public.daily_challenges(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    overall_score DECIMAL(3,1),
    completion_time_minutes INTEGER,
    responses JSONB DEFAULT '[]',
    feedback JSONB DEFAULT '{}',
    is_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, challenge_id)
);

-- =====================================================
-- TESTS & ATTEMPTS
-- =====================================================

-- Test attempts
CREATE TABLE IF NOT EXISTS public.test_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    test_type TEXT NOT NULL CHECK (test_type IN ('practice', 'mock', 'challenge')),
    test_date TIMESTAMPTZ DEFAULT NOW(),
    duration_seconds INTEGER,
    overall_score DECIMAL(3,1),
    fluency_score DECIMAL(3,1),
    grammar_score DECIMAL(3,1),
    vocabulary_score DECIMAL(3,1),
    pronunciation_score DECIMAL(3,1),
    coherence_score DECIMAL(3,1),
    questions_data JSONB DEFAULT '[]',
    audio_urls TEXT[] DEFAULT '{}',
    feedback JSONB DEFAULT '{}',
    ai_feedback TEXT,
    status TEXT DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'abandoned')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Test responses
CREATE TABLE IF NOT EXISTS public.test_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID NOT NULL REFERENCES public.test_attempts(id) ON DELETE CASCADE,
    question_id UUID REFERENCES public.questions(id),
    question_text TEXT NOT NULL,
    part INTEGER NOT NULL CHECK (part IN (1, 2, 3)),
    audio_url TEXT,
    transcript TEXT,
    duration_seconds INTEGER,
    score DECIMAL(3,1),
    feedback JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- PROGRESS & ANALYTICS
-- =====================================================

-- User progress tracking
CREATE TABLE IF NOT EXISTS public.user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    tests_completed INTEGER DEFAULT 0,
    practice_minutes INTEGER DEFAULT 0,
    average_score DECIMAL(3,1),
    skill_scores JSONB DEFAULT '{}',
    streak_days INTEGER DEFAULT 0,
    achievements_earned TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Achievements
CREATE TABLE IF NOT EXISTS public.achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    criteria JSONB DEFAULT '{}',
    points INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User achievements
CREATE TABLE IF NOT EXISTS public.user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES public.achievements(id),
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    progress DECIMAL(5,2) DEFAULT 0,
    UNIQUE(user_id, achievement_id)
);

-- =====================================================
-- SOCIAL & COMMUNITY
-- =====================================================

-- Leaderboard
CREATE TABLE IF NOT EXISTS public.leaderboard (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    period TEXT NOT NULL CHECK (period IN ('daily', 'weekly', 'monthly', 'all_time')),
    score DECIMAL(10,2) NOT NULL,
    rank INTEGER,
    tests_completed INTEGER DEFAULT 0,
    average_score DECIMAL(3,1),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, period)
);

-- User topic preferences
CREATE TABLE IF NOT EXISTS public.user_topic_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES public.question_topics(id),
    is_favorite BOOLEAN DEFAULT false,
    interest_level INTEGER DEFAULT 3 CHECK (interest_level BETWEEN 1 AND 5),
    practice_count INTEGER DEFAULT 0,
    average_score DECIMAL(3,1),
    last_practiced TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, topic_id)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_users_phone ON public.users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_test_attempts_user ON public.test_attempts(user_id, test_date DESC);
CREATE INDEX IF NOT EXISTS idx_user_progress_date ON public.user_progress(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_leaderboard_period ON public.leaderboard(period, score DESC);
CREATE INDEX IF NOT EXISTS idx_questions_topic ON public.questions(topic_id);
CREATE INDEX IF NOT EXISTS idx_daily_challenges_date ON public.daily_challenges(challenge_date);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_quotas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_topic_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Users can only see and modify their own data
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own subscriptions" ON public.user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own payments" ON public.payments
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own test attempts" ON public.test_attempts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own test attempts" ON public.test_attempts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own progress" ON public.user_progress
    FOR SELECT USING (auth.uid() = user_id);

-- Public read access for certain tables
CREATE POLICY "Public can view questions" ON public.questions
    FOR SELECT USING (is_active = true);

CREATE POLICY "Public can view topics" ON public.question_topics
    FOR SELECT USING (is_active = true);

CREATE POLICY "Public can view achievements" ON public.achievements
    FOR SELECT USING (is_active = true);

CREATE POLICY "Public can view daily challenges" ON public.daily_challenges
    FOR SELECT USING (is_active = true);

CREATE POLICY "Public can view leaderboard" ON public.leaderboard
    FOR SELECT USING (true);

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at BEFORE UPDATE ON public.user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_question_topics_updated_at BEFORE UPDATE ON public.question_topics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate user streak
CREATE OR REPLACE FUNCTION calculate_user_streak(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_streak INTEGER := 0;
    v_date DATE := CURRENT_DATE;
    v_exists BOOLEAN;
BEGIN
    LOOP
        SELECT EXISTS(
            SELECT 1 FROM public.user_progress 
            WHERE user_id = p_user_id 
            AND date = v_date 
            AND tests_completed > 0
        ) INTO v_exists;
        
        IF NOT v_exists THEN
            EXIT;
        END IF;
        
        v_streak := v_streak + 1;
        v_date := v_date - INTERVAL '1 day';
    END LOOP;
    
    RETURN v_streak;
END;
$$ LANGUAGE plpgsql;

-- Function to update leaderboard
CREATE OR REPLACE FUNCTION update_leaderboard()
RETURNS VOID AS $$
BEGIN
    -- Update daily leaderboard
    INSERT INTO public.leaderboard (user_id, period, score, tests_completed, average_score)
    SELECT 
        user_id,
        'daily',
        SUM(average_score * tests_completed) as score,
        SUM(tests_completed),
        AVG(average_score)
    FROM public.user_progress
    WHERE date = CURRENT_DATE
    GROUP BY user_id
    ON CONFLICT (user_id, period) 
    DO UPDATE SET 
        score = EXCLUDED.score,
        tests_completed = EXCLUDED.tests_completed,
        average_score = EXCLUDED.average_score,
        updated_at = NOW();
        
    -- Update ranks
    UPDATE public.leaderboard l
    SET rank = sub.rank
    FROM (
        SELECT user_id, ROW_NUMBER() OVER (ORDER BY score DESC) as rank
        FROM public.leaderboard
        WHERE period = 'daily'
    ) sub
    WHERE l.user_id = sub.user_id AND l.period = 'daily';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert default subscription plans
INSERT INTO public.subscription_plans (name, tier, price_usd, billing_period_months, monthly_test_limit, features) VALUES
('Free Trial', 'free', 0.00, 1, 3, '["3 tests per month", "Basic feedback", "Limited vocabulary exercises"]'),
('Basic Monthly', 'basic', 4.99, 1, 10, '["10 tests per month", "Detailed feedback", "All vocabulary exercises", "Basic progress tracking"]'),
('Premium Monthly', 'premium', 9.99, 1, NULL, '["Unlimited tests", "AI-powered feedback", "All features", "Priority support", "Advanced analytics"]'),
('Premium Yearly', 'premium', 79.99, 12, NULL, '["Everything in Premium Monthly", "Save 33%", "Exclusive materials", "1-on-1 coaching session"]')
ON CONFLICT DO NOTHING;

-- Insert sample achievements
INSERT INTO public.achievements (name, description, icon, points) VALUES
('First Steps', 'Complete your first test', '👶', 10),
('Streak Master', 'Maintain a 7-day streak', '🔥', 50),
('Perfect Score', 'Achieve Band 9 in any test', '🏆', 100),
('Vocabulary Wizard', 'Master 100 vocabulary items', '📚', 30),
('Speaking Marathon', 'Complete 10 tests in a day', '🏃', 40)
ON CONFLICT DO NOTHING;