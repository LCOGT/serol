def mock_lco_authenticate(request, username, password):
    return None

def mock_submit_request(params, token):
    return True, '000'

def mock_submit_request_check_proposal(params, token):
    if params['proposal'] == 'LCOEPO2018A-001':
        return True, 'XXX'
    elif params['proposal'] == 'LCOEPO2018A-002':
        return False, 'Wrong proposal'
