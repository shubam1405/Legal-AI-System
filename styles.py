"""
Minimal CSS for AI Legal Assistant - Using Streamlit defaults
Clean, simple, and focused on functionality over aesthetics.
"""

MINIMAL_CSS = """
<style>
/* Hide Streamlit footer and header elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }

/* Basic styling for consistency */
.main {
    padding: 1rem;
}

/* Simple section styling */
.metric-box {
    border: 1px solid #ddd;
    padding: 1rem;
    border-radius: 4px;
    margin: 0.5rem 0;
    background: #f9f9f9;
}

/* Simple table styling */
.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th {
    background: #f0f0f0;
    padding: 0.75rem;
    text-align: left;
    border-bottom: 2px solid #ddd;
}

.data-table td {
    padding: 0.75rem;
    border-bottom: 1px solid #ddd;
}

/* Status badge styles - simple and clean */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0 0.25rem;
}

.badge-pending {
    background: #fff3cd;
    color: #856404;
}

.badge-in-progress {
    background: #cfe2ff;
    color: #084298;
}

.badge-completed {
    background: #d1e7dd;
    color: #0f5132;
}

.badge-missing {
    background: #f8d7da;
    color: #842029;
}

.badge-included {
    background: #d1e7dd;
    color: #0f5132;
}

/* Simple card styling */
.card {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    margin: 0.5rem 0;
    background: white;
}

/* Input styling */
input, textarea, select {
    border: 1px solid #ddd;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 1rem;
}

input:focus, textarea:focus, select:focus {
    border: 2px solid #0066cc;
    outline: none;
}

/* Alert messages */
.alert {
    padding: 1rem;
    border-radius: 4px;
    margin: 0.5rem 0;
}

.alert-success {
    background: #d1e7dd;
    color: #0f5132;
    border: 1px solid #badbcc;
}

.alert-error {
    background: #f8d7da;
    color: #842029;
    border: 1px solid #f5c2c7;
}

.alert-warning {
    background: #fff3cd;
    color: #664d03;
    border: 1px solid #ffecb5;
}

.alert-info {
    background: #cfe2ff;
    color: #084298;
    border: 1px solid #b6d4fe;
}

/* Simple button styling */
button {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    background: white;
    font-size: 1rem;
    transition: all 0.2s;
}

button:hover {
    background: #f0f0f0;
    border-color: #999;
}

button.primary {
    background: #0066cc;
    color: white;
    border: 1px solid #0052a3;
}

button.primary:hover {
    background: #0052a3;
}

/* Divider */
.divider {
    border-top: 1px solid #ddd;
    margin: 1rem 0;
}

/* Text utilities */
.text-muted {
    color: #666;
    font-size: 0.9rem;
}

.text-small {
    font-size: 0.85rem;
}

.text-center {
    text-align: center;
}

</style>
"""
