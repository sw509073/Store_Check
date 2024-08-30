import os
import uuid
from flask import Blueprint, jsonify, send_file
from app.processing import process_uptime_downtime
import pandas as pd

bp = Blueprint('api', __name__)

# Ensure the REPORTS_DIR is an absolute path relative to the app root
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')

if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

@bp.route('/trigger_report', methods=['POST'])
def trigger_report():
    report_id = str(uuid.uuid4())
    report_data = process_uptime_downtime()
    
    report_file = os.path.join(REPORTS_DIR, f'{report_id}.csv')
    pd.DataFrame(report_data).to_csv(report_file, index=False)
    
    return jsonify({'report_id': report_id}), 202


@bp.route('/get_report/<report_id>', methods=['GET'])
def get_report(report_id):
    report_file = os.path.join(REPORTS_DIR, f'{report_id}.csv')
    
    print(f"Attempting to send file from: {report_file}")  # Debug statement
    
    if not os.path.isfile(report_file):
        print(f"File not found: {report_file}")  # Debug statement
        return "File not found", 404
    
    return send_file(report_file, as_attachment=True, download_name=f'{report_id}.csv')
