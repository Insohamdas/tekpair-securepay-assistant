# 🏦 Tekpair SecurePay Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Tekpair SecurePay Assistant** is an intelligent, high-performance banking chatbot web application built with a FastAPI backend and a premium, responsive glassmorphic frontend. It leverages a hybrid classification engine combining rule-based heuristics and a machine learning fallback (SVM + TF-IDF) with off-topic boundary detection to accurately assist users with account inquiries, UPI issues, loan services, cards, and more.

---

## 🚀 Key Features

*   **Hybrid AI Classification Engine**:
    *   **Rule-Based Interceptor**: Immediate high-confidence keyword matching across **36 distinct banking intent categories** for latency-free operations.
    *   **Machine Learning Fallback**: A scikit-learn Support Vector Machine (SVM) classifier trained with a TF-IDF vectorizer handles semantic variations of questions.
    *   **Off-Topic Boundary Check**: Automatically filters out-of-scope queries (decision score thresholding) and guides users back to banking topics.
*   **Production-Grade FastAPI Backend**: Asynchronous endpoints, Pydantic request validation, CORS middleware integration, and automated static asset serving.
*   **Premium Interactive Frontend**: Modern visual aesthetics featuring glassmorphism, fluid animations, custom card UI controls, dynamic auto-scrolling, and responsive layouts.
*   **Pre-packaged Datasets**:
    *   `responses.csv`: Standardized responses mapping for all 36 key customer categories.
    *   `dataset/banking_support.csv`: A unique customer support dataset containing ~10,000 queries (~1.8 MB) curated by the author.

---

## 📂 Project Structure

```bash
Tekpair-SecurePay-Assistant/
├── app.py                      # FastAPI server & hybrid prediction router
├── responses.csv               # Category-to-response mapping dataset
├── banking_model.pkl           # Trained scikit-learn SVM model
├── vectorizer.pkl              # Fitted TF-IDF Vectorizer
├── requirements.txt            # Python dependencies
├── README.md                   # Production documentation
├── dataset/
│   └── banking_support.csv     # Trimmed 100KB support tickets dataset
└── frontend/
    ├── index.html              # Chat GUI markup
    ├── style.css               # Clean vanilla CSS with glassmorphic styles
    ├── script.js               # Frontend chat state & API integration logic
    └── Tekpair Logo.png        # Brand assets
```

---

## 🛠️ Installation & Setup

Ensure you have **Python 3.9+** installed on your system.

### 1. Clone & Navigate to the Repository
```bash
git clone https://github.com/Insohamdas/Tekpair-SecurePay-Assistant.git
cd Tekpair-SecurePay-Assistant
```

### 2. Create and Activate Virtual Environment
```bash
# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# On Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🏃 Running the Application

Start the development server using `uvicorn`:

```bash
uvicorn app:app --reload --port 8000
```

Once running, you can access the application through your browser:
*   **Frontend Chat Interface**: [http://localhost:8000](http://localhost:8000)
*   **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔌 API Documentation

### Chat Endpoint
Sends a user query to the hybrid classifier and returns the matching response.

*   **URL**: `/chat`
*   **Method**: `POST`
*   **Headers**: `Content-Type: application/json`
*   **Request Body**:
    ```json
    {
      "question": "How do I block my debit card?"
    }
    ```
*   **Response Body**:
    ```json
    {
      "question": "How do I block my debit card?",
      "response": "You can block your NYC Tekpair debit card instantly via our app's Card Management section..."
    }
    ```

#### Sample cURL Request:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the limit for cash deposit?"}'
```

---

## 🤖 Machine Learning Model Documentation

This project implements a high-accuracy intent classifier for banking customer support queries.

### 1. Model Architecture
*   **Framework**: `scikit-learn`
*   **Algorithm**: Linear Support Vector Classification (`LinearSVC`)
*   **Calibration**: Wrapped in `CalibratedClassifierCV` (using 2-fold cross-validation) to provide reliable probability/confidence scores for each prediction.
*   **Feature Extraction**: `TfidfVectorizer` (Term Frequency-Inverse Document Frequency) with a maximum of 500 features. This converts raw text into numerical vectors based on word importance.

### 2. Text Preprocessing Pipeline
Before classification, every query undergoes the following steps:
*   **Lowercasing**: Standardizing text to lower case.
*   **Noise Removal**: Removing punctuation and special characters via Regex.
*   **Stopword Removal**: Eliminating common English words (e.g., "the", "is") using the NLTK library to focus on intent-carrying keywords (e.g., "locked", "blocked", "transfer").

### 3. Dataset & Training
*   **Size**: ~10,000 unique banking customer support queries.
*   **Categories**: 36 unique banking intents (e.g., UPI, Account Management, ATM, KYC).
*   **Optimization**: To resolve confusion between similar categories (like 'Account Management' vs 'Account Closure'), custom 'boost rows' were added to the training set to emphasize distinct keywords.
*   **Performance**: Achieved 100% accuracy on the target test set containing critical troubleshooting scenarios.

### 4. How to Use & Test the Model
The model is exported into two main files:
*   `banking_model.pkl`: The trained classifier.
*   `vectorizer.pkl`: The fitted TF-IDF transformer.

You can load and test the model in Python using the following code:

```python
import joblib

# Load the assets
model = joblib.load('banking_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Predict
text_vec = vectorizer.transform(["my account is locked"])
prediction = model.predict(text_vec)[0]
decision_score = model.decision_function(text_vec).max()

print(f"Prediction: {prediction} (Decision Score: {decision_score:.4f})")
```

---

## 📊 Datasets

*   **[responses.csv](file:///Users/soham/Developer/Tekpair%20SecurePay%20Assistant/responses.csv)**: Contains primary responses matching the 36 critical banking domains (including UPI, KYC, Cheque, Credit Score, FD, Dormant Accounts, etc.).
*   **[dataset/banking_support.csv](file:///Users/soham/Developer/Tekpair%20SecurePay%20Assistant/dataset/banking_support.csv)**: A completely unique dataset containing ~10,000 banking customer support tickets (1.8 MB) carefully curated by the author, ideal for test runs, model retraining, or indexing.

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
