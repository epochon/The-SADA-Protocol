"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Question {
    category: string;
    text: string;
    options: {
        A: string;
        B: string;
        C: string;
    };
}

interface RiskProfileResult {
    total_score: number;
    category: string;
    constraints: string[];
    recommendations: string[];
    completed_at: string;
}

const RiskProfileQuestionnaire = () => {
    const [currentStep, setCurrentStep] = useState(0);
    const [answers, setAnswers] = useState<Record<string, string>>({});
    const [result, setResult] = useState<RiskProfileResult | null>(null);
    const [loading, setLoading] = useState(false);

    const questions: Record<string, Question> = {
        Q1: {
            category: "Financial Stability",
            text: "How stable is your income?",
            options: {
                A: "Very stable (salaried, government job)",
                B: "Somewhat stable (regular business income)",
                C: "Unpredictable (freelance, commission-based)"
            }
        },
        Q2: {
            category: "Financial Stability",
            text: "Do you have insurance and 3-6 months emergency fund?",
            options: {
                A: "Yes, fully covered",
                B: "Partially covered",
                C: "No, not yet"
            }
        },
        Q3: {
            category: "Goals & Time Horizon",
            text: "What is your primary investment objective?",
            options: {
                A: "Capital protection (preserve wealth)",
                B: "Balanced growth (moderate returns)",
                C: "Maximum growth (aggressive returns)"
            }
        },
        Q4: {
            category: "Experience",
            text: "How familiar are you with financial markets?",
            options: {
                A: "Beginner (just starting)",
                B: "Some experience (1-3 years)",
                C: "Comfortable (3+ years, understand volatility)"
            }
        },
        Q5: {
            category: "Volatility Tolerance",
            text: "What's the maximum drop you can tolerate?",
            options: {
                A: "5-10% (very low tolerance)",
                B: "10-25% (moderate tolerance)",
                C: "25-40% (high tolerance)"
            }
        },
        Q6: {
            category: "Volatility Tolerance",
            text: "How long can you stay invested if value drops?",
            options: {
                A: "Less than 1 year",
                B: "1-3 years",
                C: "3-5+ years (long-term horizon)"
            }
        },
        Q7: {
            category: "Volatility Tolerance",
            text: "How would you feel during a market crash?",
            options: {
                A: "Very stressed, would lose sleep",
                B: "Stressed but manageable",
                C: "Comfortable, see it as opportunity"
            }
        },
        Q8: {
            category: "Behavior in Downturns",
            text: "What would you do if your investment fell 20%?",
            options: {
                A: "Sell immediately to prevent further loss",
                B: "Hold and wait for recovery",
                C: "Buy more (averaging down)"
            }
        },
        Q9: {
            category: "Behavior in Downturns",
            text: "If your SIP is down, would you continue?",
            options: {
                A: "Stop SIP immediately",
                B: "Continue with discomfort",
                C: "Continue confidently (rupee cost averaging)"
            }
        }
    };

    const questionKeys = Object.keys(questions);
    const totalQuestions = questionKeys.length;
    const currentQuestionKey = questionKeys[currentStep];
    const currentQuestion = questions[currentQuestionKey];

    const handleAnswer = (answer: string) => {
        setAnswers({ ...answers, [currentQuestionKey]: answer });

        if (currentStep < totalQuestions - 1) {
            setTimeout(() => setCurrentStep(currentStep + 1), 300);
        }
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/hypeslayer/submit-questionnaire', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answers })
            });

            const data = await response.json();
            setResult(data.profile);

            // Save to localStorage for persistence
            localStorage.setItem('hypeslayer-risk-profile', JSON.stringify(data.profile));
        } catch (error) {
            console.error('Error submitting questionnaire:', error);
            alert('Failed to submit questionnaire. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handlePrevious = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const progress = ((currentStep + 1) / totalQuestions) * 100;

    if (result) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="max-w-2xl w-full bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl"
                >
                    <div className="text-center mb-8">
                        <div className="inline-block p-4 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full mb-4">
                            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <h2 className="text-4xl font-bold text-white mb-2">Profile Complete!</h2>
                        <p className="text-gray-300">Your personalized investment profile is ready</p>
                    </div>

                    <div className="space-y-6">
                        <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-2xl font-bold text-white">{result.category}</h3>
                                <span className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                                    {result.total_score}/27
                                </span>
                            </div>

                            <div className="h-3 bg-white/10 rounded-full overflow-hidden mb-6">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${(result.total_score / 27) * 100}%` }}
                                    transition={{ duration: 1, ease: "easeOut" }}
                                    className={`h-full rounded-full ${result.category === 'Conservative' ? 'bg-blue-500' :
                                            result.category === 'Moderate' ? 'bg-yellow-500' :
                                                'bg-red-500'
                                        }`}
                                />
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <h4 className="text-sm font-semibold text-gray-400 uppercase mb-2">Recommendations</h4>
                                    <ul className="space-y-2">
                                        {result.recommendations.map((rec, i) => (
                                            <li key={i} className="text-gray-200 flex items-start">
                                                <span className="text-green-400 mr-2">✓</span>
                                                <span>{rec}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                <div>
                                    <h4 className="text-sm font-semibold text-gray-400 uppercase mb-2">Investment Constraints</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {result.constraints.map((constraint, i) => (
                                            <span
                                                key={i}
                                                className="px-3 py-1 bg-red-500/20 text-red-300 rounded-full text-sm border border-red-500/30"
                                            >
                                                {constraint.replace(/_/g, ' ')}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={() => window.location.reload()}
                            className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-purple-500/50 transition-all"
                        >
                            Start Analyzing Videos
                        </button>
                    </div>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
            <div className="max-w-3xl w-full">
                {/* Progress Bar */}
                <div className="mb-8">
                    <div className="flex justify-between text-sm text-gray-400 mb-2">
                        <span>Question {currentStep + 1} of {totalQuestions}</span>
                        <span>{Math.round(progress)}% Complete</span>
                    </div>
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ duration: 0.3 }}
                            className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                        />
                    </div>
                </div>

                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentStep}
                        initial={{ opacity: 0, x: 50 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -50 }}
                        transition={{ duration: 0.3 }}
                        className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl"
                    >
                        <div className="mb-8">
                            <span className="inline-block px-4 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm font-semibold mb-4 border border-purple-500/30">
                                {currentQuestion.category}
                            </span>
                            <h2 className="text-3xl font-bold text-white mb-2">
                                {currentQuestion.text}
                            </h2>
                            <p className="text-gray-400">Select the option that best describes you</p>
                        </div>

                        <div className="space-y-4 mb-8">
                            {Object.entries(currentQuestion.options).map(([key, value]) => (
                                <motion.button
                                    key={key}
                                    onClick={() => handleAnswer(key)}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    className={`w-full p-6 text-left rounded-2xl border-2 transition-all ${answers[currentQuestionKey] === key
                                            ? 'bg-purple-500/30 border-purple-400 shadow-lg shadow-purple-500/30'
                                            : 'bg-white/5 border-white/10 hover:border-white/30 hover:bg-white/10'
                                        }`}
                                >
                                    <div className="flex items-center">
                                        <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center mr-4 ${answers[currentQuestionKey] === key
                                                ? 'border-purple-400 bg-purple-500'
                                                : 'border-gray-500'
                                            }`}>
                                            {answers[currentQuestionKey] === key && (
                                                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                </svg>
                                            )}
                                        </div>
                                        <div>
                                            <div className="font-semibold text-white mb-1">Option {key}</div>
                                            <div className="text-gray-300">{value}</div>
                                        </div>
                                    </div>
                                </motion.button>
                            ))}
                        </div>

                        <div className="flex gap-4">
                            {currentStep > 0 && (
                                <button
                                    onClick={handlePrevious}
                                    className="px-6 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-all border border-white/20"
                                >
                                    ← Previous
                                </button>
                            )}

                            {currentStep === totalQuestions - 1 && answers[currentQuestionKey] && (
                                <button
                                    onClick={handleSubmit}
                                    disabled={loading}
                                    className="flex-1 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-purple-500/50 transition-all disabled:opacity-50"
                                >
                                    {loading ? 'Analyzing...' : 'Get My Profile →'}
                                </button>
                            )}
                        </div>
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    );
};

export default RiskProfileQuestionnaire;
