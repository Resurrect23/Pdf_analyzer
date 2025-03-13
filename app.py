import os
import google.generativeai as genai
from flask import Flask, request, render_template, redirect, url_for
from PyPDF2 import PdfReader

# GOOGLE GEMINI API
GENAI_API_KEY = "AIzaSyDVejqQheNyZdV6lcQiMXUqan4hp9YpSig"
genai.configure(api_key=GENAI_API_KEY)

# FLASK APP
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# FUNCTION TO EXTRACT TEXT FROM PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip()

# INTERACTION WITH GEMINI API
def ask_gemini(question, context):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(f"Answer this based on context:\n\n{context}\n\nQuestion: {question}")
    return response.text if response else "No answer found."

# ROUTE : UPLOAD PDF AND ASK QUESTIONS
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("pdf")
        question = request.form.get("question")

        if not file or not question:
            return "Error: Missing file or question.", 400

        if not file.filename.endswith(".pdf"):
            return "Error: Only PDF files are allowed.", 400

        # Save the file
        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(pdf_path)

        # Extract text from the PDF
        pdf_text = extract_text_from_pdf(pdf_path)

        # Get answer from Gemini AI
        answer = ask_gemini(question, pdf_text)

        return redirect(url_for("result", answer=answer))

    return render_template("index.html")

@app.route("/result")
def result():
    answer = request.args.get("answer", "No answer found.")
    return render_template("result.html", answer=answer)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
