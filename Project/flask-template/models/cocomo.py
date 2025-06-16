def basic_cocomo(kloc, project_type='organic'):
    """
    Basic COCOMO model calculation
    
    project_type: 'organic' (simple), 'semi-detached' (medium), 'embedded' (complex)
    """
    coefficients = {
        'organic': (2.4, 1.05),
        'semi-detached': (3.0, 1.12),
        'embedded': (3.6, 1.20)
    }
    
    a, b = coefficients.get(project_type, coefficients['organic'])
    
    # Effort in person-months
    effort = a * (kloc ** b)
    
    # Development time in months
    dev_time = 2.5 * (effort ** 0.38)
    
    return {
        'effort': round(effort, 2),
        'dev_time': round(dev_time, 2),
        'staff': round(effort / dev_time, 2)
    }