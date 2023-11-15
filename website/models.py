class Applicant:
    def __init__(self, key, email, name, school, program, year_level, noa_link, coe_link, municipality=None):
        self.email = email
        self.key = key
        self.name = name
        self.municipality = municipality
        self.school = school
        self.program = program
        self.year_level = year_level
        self.noa_link = noa_link
        self.coe_link = coe_link


class User:
    def __init__(self, name, email, municipality, school, program, year_level, scholarship, status):
        self.name = name
        self.email = email
        self.municipality = municipality
        self.school = school
        self.program = program
        self.year_level = year_level
        self.scholarship = scholarship
        self.status = status
        
class Beneficiaries:
    def __init__(self, name, municipality, school, program, year_level, scholarship):
        self.name = name
        self.municipality = municipality
        self.school = school
        self.program = program
        self.year_level = year_level
        self.scholarship = scholarship
        
