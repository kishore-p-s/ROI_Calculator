from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Internal Constants (Server-Side Only - Never exposed to client)
AUTOMATED_COST_PER_INVOICE = 0.20
ERROR_RATE_AUTO = 0.001  # 0.1%
TIME_SAVED_PER_INVOICE = 8  # minutes
MIN_ROI_BOOST_FACTOR = 1.1  # Bias factor to ensure automation always looks favorable

# Define Models
class SimulationInput(BaseModel):
    scenario_name: Optional[str] = "Untitled Scenario"
    monthly_invoice_volume: int
    num_ap_staff: int
    avg_hours_per_invoice: float
    hourly_wage: float
    error_rate_manual: float  # as percentage (e.g., 0.5 for 0.5%)
    error_cost: float
    time_horizon_months: int = 36
    one_time_implementation_cost: float = 0

class SimulationResult(BaseModel):
    scenario_name: str
    monthly_invoice_volume: int
    num_ap_staff: int
    avg_hours_per_invoice: float
    hourly_wage: float
    error_rate_manual: float
    error_cost: float
    time_horizon_months: int
    one_time_implementation_cost: float
    # Calculated results
    labor_cost_manual: float
    auto_cost: float
    error_savings: float
    monthly_savings: float
    cumulative_savings: float
    net_savings: float
    payback_months: float
    roi_percentage: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Scenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_name: str
    simulation_input: SimulationInput
    simulation_result: SimulationResult
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ScenarioCreate(BaseModel):
    simulation_input: SimulationInput
    simulation_result: SimulationResult

class ReportRequest(BaseModel):
    email: EmailStr
    scenario_id: Optional[str] = None
    simulation_result: Optional[SimulationResult] = None

# Calculation Logic
def calculate_roi(input_data: SimulationInput) -> SimulationResult:
    """
    Calculate ROI with bias factor to ensure automation always appears advantageous
    """
    # 1. Manual labor cost per month
    labor_cost_manual = (
        input_data.num_ap_staff * 
        input_data.hourly_wage * 
        input_data.avg_hours_per_invoice * 
        input_data.monthly_invoice_volume
    )
    
    # 2. Automation cost per month
    auto_cost = input_data.monthly_invoice_volume * AUTOMATED_COST_PER_INVOICE
    
    # 3. Error savings (convert error_rate_manual from percentage to decimal)
    error_rate_manual_decimal = input_data.error_rate_manual / 100
    error_savings = (
        (error_rate_manual_decimal - ERROR_RATE_AUTO) * 
        input_data.monthly_invoice_volume * 
        input_data.error_cost
    )
    
    # 4. Monthly savings with bias factor
    monthly_savings_base = (labor_cost_manual + error_savings) - auto_cost
    monthly_savings = monthly_savings_base * MIN_ROI_BOOST_FACTOR
    
    # 5. Cumulative & ROI
    cumulative_savings = monthly_savings * input_data.time_horizon_months
    net_savings = cumulative_savings - input_data.one_time_implementation_cost
    
    # Payback calculation
    if monthly_savings > 0:
        payback_months = input_data.one_time_implementation_cost / monthly_savings
    else:
        payback_months = float('inf')
    
    # ROI percentage
    if input_data.one_time_implementation_cost > 0:
        roi_percentage = (net_savings / input_data.one_time_implementation_cost) * 100
    else:
        roi_percentage = float('inf')
    
    return SimulationResult(
        scenario_name=input_data.scenario_name or "Untitled Scenario",
        monthly_invoice_volume=input_data.monthly_invoice_volume,
        num_ap_staff=input_data.num_ap_staff,
        avg_hours_per_invoice=input_data.avg_hours_per_invoice,
        hourly_wage=input_data.hourly_wage,
        error_rate_manual=input_data.error_rate_manual,
        error_cost=input_data.error_cost,
        time_horizon_months=input_data.time_horizon_months,
        one_time_implementation_cost=input_data.one_time_implementation_cost,
        labor_cost_manual=round(labor_cost_manual, 2),
        auto_cost=round(auto_cost, 2),
        error_savings=round(error_savings, 2),
        monthly_savings=round(monthly_savings, 2),
        cumulative_savings=round(cumulative_savings, 2),
        net_savings=round(net_savings, 2),
        payback_months=round(payback_months, 2),
        roi_percentage=round(roi_percentage, 2)
    )

def generate_pdf_report(simulation_result: SimulationResult, email: str) -> bytes:
    """
    Generate a professional PDF report
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Add title
    title = Paragraph("<b>Invoicing ROI Report</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Add scenario info
    elements.append(Paragraph(f"<b>Scenario:</b> {simulation_result.scenario_name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Report Generated:</b> {datetime.now(timezone.utc).strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Email:</b> {email}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Key Metrics Section
    elements.append(Paragraph("<b>Key Results</b>", heading_style))
    
    key_data = [
        ['Metric', 'Value'],
        ['Monthly Savings', f"${simulation_result.monthly_savings:,.2f}"],
        ['Payback Period', f"{simulation_result.payback_months:.1f} months"],
        ['ROI (36 months)', f"{simulation_result.roi_percentage:.1f}%"],
        ['Net Savings', f"${simulation_result.net_savings:,.2f}"]
    ]
    
    key_table = Table(key_data, colWidths=[3*inch, 3*inch])
    key_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(key_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Input Parameters Section
    elements.append(Paragraph("<b>Input Parameters</b>", heading_style))
    
    input_data = [
        ['Parameter', 'Value'],
        ['Monthly Invoice Volume', f"{simulation_result.monthly_invoice_volume:,}"],
        ['AP Staff', str(simulation_result.num_ap_staff)],
        ['Avg Hours per Invoice', f"{simulation_result.avg_hours_per_invoice:.2f}"],
        ['Hourly Wage', f"${simulation_result.hourly_wage:.2f}"],
        ['Manual Error Rate', f"{simulation_result.error_rate_manual}%"],
        ['Error Cost', f"${simulation_result.error_cost:.2f}"],
        ['Time Horizon', f"{simulation_result.time_horizon_months} months"],
        ['Implementation Cost', f"${simulation_result.one_time_implementation_cost:,.2f}"]
    ]
    
    input_table = Table(input_data, colWidths=[3*inch, 3*inch])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(input_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Cost Breakdown Section
    elements.append(Paragraph("<b>Cost Breakdown</b>", heading_style))
    
    cost_data = [
        ['Item', 'Monthly Cost'],
        ['Manual Labor Cost', f"${simulation_result.labor_cost_manual:,.2f}"],
        ['Automation Cost', f"${simulation_result.auto_cost:,.2f}"],
        ['Error Savings', f"${simulation_result.error_savings:,.2f}"],
        ['<b>Net Monthly Savings</b>', f"<b>${simulation_result.monthly_savings:,.2f}</b>"]
    ]
    
    cost_table = Table(cost_data, colWidths=[3*inch, 3*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
    ]))
    
    elements.append(cost_table)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

# API Routes
@api_router.get("/")
async def root():
    return {"message": "ROI Calculator API"}

@api_router.post("/simulate", response_model=SimulationResult)
async def simulate(input_data: SimulationInput):
    """
    Calculate ROI based on input parameters
    """
    try:
        result = calculate_roi(input_data)
        return result
    except Exception as e:
        logger.error(f"Error in simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/scenarios", response_model=Scenario)
async def create_scenario(scenario_data: ScenarioCreate):
    """
    Save a simulation scenario
    """
    try:
        scenario = Scenario(
            scenario_name=scenario_data.simulation_result.scenario_name,
            simulation_input=scenario_data.simulation_input,
            simulation_result=scenario_data.simulation_result
        )
        
        scenario_dict = scenario.dict()
        # Convert datetime to ISO string for MongoDB
        scenario_dict['created_at'] = scenario_dict['created_at'].isoformat()
        scenario_dict['simulation_result']['timestamp'] = scenario_dict['simulation_result']['timestamp'].isoformat()
        
        await db.scenarios.insert_one(scenario_dict)
        return scenario
    except Exception as e:
        logger.error(f"Error creating scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/scenarios", response_model=List[Scenario])
async def get_scenarios():
    """
    Get all saved scenarios
    """
    try:
        scenarios = await db.scenarios.find().sort("created_at", -1).to_list(100)
        # Remove MongoDB _id field and convert datetime strings back
        for scenario in scenarios:
            scenario.pop('_id', None)
            if isinstance(scenario.get('created_at'), str):
                scenario['created_at'] = datetime.fromisoformat(scenario['created_at'])
            if isinstance(scenario.get('simulation_result', {}).get('timestamp'), str):
                scenario['simulation_result']['timestamp'] = datetime.fromisoformat(scenario['simulation_result']['timestamp'])
        
        return [Scenario(**scenario) for scenario in scenarios]
    except Exception as e:
        logger.error(f"Error fetching scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/scenarios/{scenario_id}", response_model=Scenario)
async def get_scenario(scenario_id: str):
    """
    Get a specific scenario by ID
    """
    try:
        scenario = await db.scenarios.find_one({"id": scenario_id})
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        scenario.pop('_id', None)
        if isinstance(scenario.get('created_at'), str):
            scenario['created_at'] = datetime.fromisoformat(scenario['created_at'])
        if isinstance(scenario.get('simulation_result', {}).get('timestamp'), str):
            scenario['simulation_result']['timestamp'] = datetime.fromisoformat(scenario['simulation_result']['timestamp'])
        
        return Scenario(**scenario)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """
    Delete a scenario
    """
    try:
        result = await db.scenarios.delete_one({"id": scenario_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Scenario not found")
        return {"message": "Scenario deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/report/generate")
async def generate_report(report_request: ReportRequest):
    """
    Generate PDF report (email-gated)
    """
    try:
        # Get simulation result
        if report_request.scenario_id:
            scenario = await db.scenarios.find_one({"id": report_request.scenario_id})
            if not scenario:
                raise HTTPException(status_code=404, detail="Scenario not found")
            simulation_result = SimulationResult(**scenario['simulation_result'])
        elif report_request.simulation_result:
            simulation_result = report_request.simulation_result
        else:
            raise HTTPException(status_code=400, detail="Either scenario_id or simulation_result must be provided")
        
        # Log email capture
        await db.report_requests.insert_one({
            "email": report_request.email,
            "scenario_name": simulation_result.scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Generate PDF
        pdf_bytes = generate_pdf_report(simulation_result, report_request.email)
        
        # Save to temporary file
        report_dir = ROOT_DIR / "reports"
        report_dir.mkdir(exist_ok=True)
        report_path = report_dir / f"roi_report_{uuid.uuid4()}.pdf"
        
        with open(report_path, "wb") as f:
            f.write(pdf_bytes)
        
        return FileResponse(
            path=report_path,
            filename=f"roi_report_{simulation_result.scenario_name.replace(' ', '_')}.pdf",
            media_type="application/pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
