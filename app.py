from pathlib import Path
import csv
import joblib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Load model and vectorizer
model = joblib.load(BASE_DIR / "banking_model.pkl")
vectorizer = joblib.load(BASE_DIR / "vectorizer.pkl")

# Load responses from CSV
responses = {}
responses_path = BASE_DIR / "responses.csv"
if responses_path.exists():
    with open(responses_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                responses[row[0].strip()] = row[1].strip()

# High-Confidence Intent Keyword Mapping Table (All 36 categories)
INTENT_KEYWORDS = {
    "Account Closure": ["close account", "account closure", "close my account", "closure request", "deactivate account", "terminate account"],
    "Address Update": ["address", "change address", "update address", "location update", "postal address", "communication address"],
    "BBPS": ["bbps", "bill payment", "utility bill", "electricity bill", "water bill", "gas bill", "dth recharge"],
    "Beneficiary Management": ["beneficiary", "add payee", "payee", "cooling-off", "add beneficiary", "transfer beneficiary"],
    "Cash Deposit": ["cash deposit", "deposit cash", "cdm", "deposit machine", "deposit limit"],
    "Cheque": ["cheque", "checkbook", "chequebook", "stop cheque", "clearing", "leaflets"],
    "Credit Card": ["credit card", "credit cards", "limit upgrade", "cc statement", "card billing"],
    "Credit Score": ["credit score", "cibil", "credit rating", "check score", "cibil report"],
    "Current Account": ["current account", "business account", "trade account", "sole proprietorship"],
    "Debit Card": ["debit card", "atm card", "rupay", "visa card", "mastercard", "block card", "lost card"],
    "Demat Account": ["demat", "trading account", "stock market", "invest in shares", "shares", "ipo"],
    "Dormant Account": ["dormant", "inactive account", "reactivate account", "unoperated account"],
    "E-Statements": ["statement", "e-statement", "account statement", "download statement", "transaction history"],
    "Education Loan": ["education loan", "study loan", "student loan", "vidyasaarathi", "study abroad"],
    "FASTag": ["fastag", "toll payment", "highway toll", "recharge fastag"],
    "FD & RD": ["fixed deposit", "recurring deposit", "fd interest", "rd interest", "term deposit"],
    "Fraud & Security": ["fraud", "unauthorized", "stolen", "compromised", "scam", "suspicious", "hacked", "freeze account"],
    "Insurance": ["insurance", "life policy", "health insurance", "motor policy", "travel insurance"],
    "Interest & Charges": ["interest rate", "minimum balance", "penalty", "charges", "hidden fees", "annual fee"],
    "International Banking": ["swift", "remittance", "forex", "international card", "nro", "nre", "wire transfer"],
    "KYC": ["kyc", "documents", "aadhaar", "pan card", "video kyc", "know your customer"],
    "Loans": ["loan", "home loan", "personal loan", "car loan", "mortgage", "emi check"],
    "Locker Services": ["locker", "safe deposit", "branch locker", "safe vault"],
    "Merchant Payments": ["merchant", "bharat qr", "scan qr", "shop payment", "vendor payment"],
    "Mobile Banking": ["mobile app", "activate app", "m-banking", "mobile banking", "app registration"],
    "Mutual Funds": ["mutual fund", "sip", "investment plan", "lump sum", "mutual funds"],
    "NRI Banking": ["nri", "non-resident", "nre account", "nro account", "fcnr"],
    "Net Banking": ["netbanking", "net banking", "internet banking", "desktop banking", "login issue"],
    "Nominee Services": ["nominee", "add nominee", "update nominee", "succession"],
    "Rewards": ["reward points", "edge points", "redeem points", "rewards desk", "cashback"],
    "SMS & Alerts": ["sms alert", "notifications", "email alert", "push updates"],
    "Savings Account": ["savings account", "open savings", "interest savings", "saving account"],
    "Senior Citizen Services": ["senior citizen", "doorstep banking", "pensioner", "priority branch"],
    "Standing Instructions": ["standing instruction", "si mandate", "auto-pay", "automated transfer", "mandate"],
    "Tax & TDS": ["tds", "form 16", "form 15g", "form 15h", "tax exemption", "income tax"],
    "UPI": ["upi", "failed upi", "payment failed", "bhim", "gpay", "phonepe", "rrn", "double debit", "debited twice"]
}

app = FastAPI(title="Banking Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/chat")
def chat(request: ChatRequest):
    question_lower = request.question.lower().strip()
    response_text = None
    matched_intent = None

    # Greeting Interceptor
    if question_lower in ["hello", "hi", "hey", "namaste", "good morning", "good afternoon"]:
        response_text = "Namaste! Welcome to NYC Tekpair Bharat support desk. How can I assist you with your banking services today?"

    # 1. Rule-Based Intent Interceptor (High-Confidence Keywords check across all 36 classes)
    if not response_text:
        for intent, keywords in INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in question_lower:
                    matched_intent = intent
                    break
            if matched_intent:
                break

        # If we matched a keyword, fetch the response from our responses map
        if matched_intent:
            # Specific structural/text overrides for prompts
            if matched_intent == "UPI" and ("double debit" in question_lower or "debited twice" in question_lower or "twice debited" in question_lower):
                response_text = "If your account has been debited twice for a single transaction, the secondary charge is held in transit and will be auto-refunded to your account by the routing bank within 48 to 72 hours. If it does not reflect, please raise a ticket under the 'Dispute Desk' using the reference number."
            elif matched_intent == "Savings Account" and ("check balance" in question_lower or "account balance" in question_lower or "check my balance" in question_lower):
                response_text = "To check your NYC Tekpair account balance, you can:\n1. Send SMS 'BAL' to +91 9876543210 from your registered mobile number.\n2. Give a missed call to 1800-102-BANK.\n3. Log into the NYC Tekpair Bharat mobile app or Netbanking portal to view your real-time ledger."
            else:
                response_text = responses.get(matched_intent)

    # 2. ML Fallback (TF-IDF Vectorizer + SVM Model with Off-Topic Decision Boundary check)
    if not response_text:
        features = vectorizer.transform([request.question])
        
        # Check decision score confidence
        decision_score = model.decision_function(features).max()
        
        if decision_score < -0.80:
            response_text = "I am sorry, but I can only assist you with banking and account-related queries for NYC Tekpair Bharat. Please ask a question related to UPI, cards, loans, or checkbook services."
        else:
            prediction = model.predict(features)[0]
            response_text = responses.get(
                prediction,
                "I am sorry, I couldn't process your request. Please connect with our support desk."
            )

    return {
        "question": request.question,
        "response": response_text
    }
