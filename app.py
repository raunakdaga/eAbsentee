from flask import Flask, render_template, request, redirect, session, send_file, make_response
from functions import application_process, add_to_campaign
from keys import SECRET_KEY
import os
import json

# Sets CWD to whatever directory app.py is located in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Initialize flask app, SECRET_KEY can be found in keys.py
app = Flask(__name__, template_folder="templates")
app.secret_key = SECRET_KEY
app.root_path = os.path.dirname(os.path.abspath(__file__))
app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.config['EXPLAIN_TEMPLATE_LOADING'] = True


'''Static Routes'''
# Homepage
@app.route('/')
def home():
    return render_template('index.html')


# Error
@app.route('/error/', methods=['GET'])
def error_page():
    return render_template('formerror.html')


# Credits
@app.route('/credits/', methods=['GET'])
def credits_page():
    return render_template('credits.html')


# Fillable Form as .PDF
@app.route('/fillableform/')
def render_fillableform_pdf():
    return send_file(
        open('static/blankAppFillable.pdf', 'rb'),
        attachment_filename='blankAppFillable.pdf'
    )

# Printable Form as .PDF
@app.route('/printform/')
def render_printform_pdf():
    return send_file(
        open('static/blankApp.pdf', 'rb'),
        attachment_filename='blankApp.pdf'
    )


@app.route('/videocredits/')
def render_videocredits_pdf():
    return send_file(
        open('static/credits.pdf', 'rb'),
        attachment_filename='credits.pdf'
    )

# List of Counties for API
@app.route('/listcounty/')
def list_of_counties():
    return(render_template('list_of_counties.html'))

# About
@app.route('/about/')
def about():
    return(render_template('about.html'))

# 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/form/', methods=['POST', 'GET'])
def process_form():
    """ Form Route: Returns form when requested,
    collects data from user when inputted. The data is sent to
    functions.py, where it is parsed and converted,
    built into the PDF, and emailed to the respective registar. If
    unable to send the PDF, an error page is returned. """
    if request.method == 'POST':
        # try:
        application_process(request)
        # except(Exception):
        #     return redirect('/error/')
        return redirect('/confirmation/')
    else:
        if 'campaign' in request.cookies:
            with open('static/campaigns.json') as file:
                campaigns = json.load(file)
                campaign_id = campaigns[request.cookies.get('campaign')]
                campaign_name = campaign_id['name']
                return render_template(('form_' + campaign_name + '.html'))
        return render_template('form.html')


# This route sets the county cookies. It is used to determine which form to display. The different forms can have different counties displayed.
@app.route('/cou/<campaign>')
def home_with_campaign(campaign: str):
    response = make_response(redirect('/'))
    response.set_cookie('campaign', campaign, max_age=60*60*24*365*2)
    return response


# Sets group cookies - determines which group the users came from
@app.route('/group/<group>')
def set_channel(group: str):
    response = make_response(redirect('/'))
    response.set_cookie('group', group, max_age=60*60*24*365*2)
    return response


# TODO: Redirect to page based off of succesful submission
@app.route('/confirmation/', methods=['GET'])
def confirmation_page():
    """Confirmation Route: user is redirected here
    after submission of form. """
    # return render_template('confirmation.html')
    # if session.get('output_pdf') is not None:
    return render_template('confirmation.html')
    # else:
    #     # TODO: redirect to more appropriate error page (like 403 forbidden)
    #     return redirect('/404/')


# Displays application to user in PDF form
@app.route('/applications/<id>.pdf')
def render_pdf(id: str):
    return send_file(
        open(session['output_file'], 'rb'),
        attachment_filename=session['output_file']
    )


@app.route('/api/', methods=['POST', 'GET'])
def api():
    if request.method == 'POST':
        add_to_campaign(request)
        return render_template('api.html', confirmation='Confirmed! ' + request.form.get('campaign_name') + 'has been added to the list of campaigns.')
    else:
        return render_template('api.html')


if __name__ == '__main__':
    app.run()
