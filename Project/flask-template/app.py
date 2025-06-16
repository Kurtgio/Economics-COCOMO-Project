from flask import Flask, render_template, request, jsonify, send_file
from models.cocomo import basic_cocomo
from models.financial import calculate_roi, calculate_npv, calculate_payback_period
from models.risk import calculate_risk_score, risk_category
import io
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/api/cocomo", methods=["POST"])
def cocomo_calculation():
    data = request.json
    kloc = float(data.get("kloc", 0))
    project_type = data.get("project_type", "organic")

    result = basic_cocomo(kloc, project_type)

    return jsonify(result)


@app.route("/api/financial", methods=["POST"])
def financial_calculation():
    data = request.json
    cost = float(data.get("cost", 0))
    annual_benefit = float(data.get("annual_benefit", 0))
    years = int(data.get("years", 1))
    discount_rate = float(data.get("discount_rate", 0.1))

    roi = calculate_roi(cost, annual_benefit, years)
    npv = calculate_npv(cost, annual_benefit, discount_rate, years)
    payback = calculate_payback_period(cost, annual_benefit)

    return jsonify(
        {
            "roi": roi,
            "npv": npv,
            "payback": payback,
        }
    )


@app.route("/api/risk", methods=["POST"])
def risk_calculation():
    data = request.json
    risks = data.get("risks", [])

    risk_results = []
    for risk in risks:
        probability = int(risk.get("probability", 1))
        impact = int(risk.get("impact", 1))

        score = calculate_risk_score(probability, impact)
        category = risk_category(score)

        risk_results.append(
            {
                "name": risk.get("name", "Unnamed Risk"),
                "score": score,
                "category": category,
            }
        )

    return jsonify({"risks": risk_results})


@app.route("/generate-report")
def generate_report():
    # Get parameters from URL
    kloc = float(request.args.get("kloc", 0) or 0)
    project_type = request.args.get("project_type", "organic")
    cost = float(request.args.get("cost", 0) or 0)
    annual_benefit = float(request.args.get("annual_benefit", 0) or 0)
    years = int(request.args.get("years", 5) or 5)
    discount_rate = float(request.args.get("discount_rate", 0.1) or 0.1)
    
    # Calculate values
    cocomo_result = basic_cocomo(kloc, project_type)
    roi = calculate_roi(cost, annual_benefit, years)
    npv = calculate_npv(cost, annual_benefit, discount_rate, years)
    payback = calculate_payback_period(cost, annual_benefit)
    
    # Process risks
    risks_data = []
    if request.args.get("risks"):
        risks_param = request.args.get("risks").split(",")
        for risk_item in risks_param:
            parts = risk_item.split("|")
            if len(parts) == 3:
                name, probability, impact = parts
                score = calculate_risk_score(int(probability), int(impact))
                category = risk_category(score)
                risks_data.append({"name": name, "score": score, "category": category})
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Software Project Economic Analysis Report", 0, 1, "C")
    
    # Date
    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1, "R")
    
    # COCOMO Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "COCOMO Estimation", 0, 1, "L")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 10, "Project Size (KLOC):", 0, 0)
    pdf.cell(100, 10, f"{kloc}", 0, 1)
    
    pdf.cell(100, 10, "Project Type:", 0, 0)
    pdf.cell(100, 10, f"{project_type}", 0, 1)
    
    pdf.cell(100, 10, "Effort (person-months):", 0, 0)
    pdf.cell(100, 10, f"{cocomo_result['effort']}", 0, 1)
    
    pdf.cell(100, 10, "Development Time (months):", 0, 0)
    pdf.cell(100, 10, f"{cocomo_result['dev_time']}", 0, 1)
    
    pdf.cell(100, 10, "Average Staff:", 0, 0)
    pdf.cell(100, 10, f"{cocomo_result['staff']}", 0, 1)
    
    # Financial Analysis Section
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Financial Analysis", 0, 1, "L")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 10, "ROI:", 0, 0)
    pdf.cell(100, 10, f"{roi}%", 0, 1)
    
    pdf.cell(100, 10, "NPV:", 0, 0)
    pdf.cell(100, 10, f"EUR {npv}", 0, 1)
    
    pdf.cell(100, 10, "Payback Period:", 0, 0)
    pdf.cell(100, 10, f"{payback} years", 0, 1)
    
    # Risk Analysis Section
    if risks_data:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Risk Analysis", 0, 1, "L")
        
        pdf.set_font("Arial", "", 10)
        # Table header
        pdf.cell(80, 10, "Risk", 1, 0, "C")
        pdf.cell(40, 10, "Score", 1, 0, "C")
        pdf.cell(40, 10, "Category", 1, 1, "C")
        
        # Table rows with actual data
        for risk in risks_data:
            pdf.cell(80, 10, risk["name"], 1, 0)
            pdf.cell(40, 10, str(risk["score"]), 1, 0)
            pdf.cell(40, 10, risk["category"], 1, 1)
    
    # Generate in-memory PDF
    pdf_output = io.BytesIO()
    pdf_content = pdf.output(dest='S')  # 'S' means return as string
    pdf_output.write(pdf_content.encode('latin1') if isinstance(pdf_content, str) else pdf_content)
    pdf_output.seek(0)
    
    return send_file(
        pdf_output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="software_project_analysis.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
