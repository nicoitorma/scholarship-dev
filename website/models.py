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


class Student:
    def __init__(self, name=None, role=None, email=None, municipality=None, school=None, program=None, year_level=None, scholarship=None, status=None):
        self.name = name
        self.role = role
        self.email = email
        self.municipality = municipality
        self.school = school
        self.program = program
        self.year_level = year_level
        self.scholarship = scholarship
        self.status = status


class Beneficiaries:
    def __init__(self, email, name, municipality, school, program, year_level, scholarship, coe, cog):
        self.email = email
        self.name = name
        self.municipality = municipality
        self.school = school
        self.program = program
        self.year_level = year_level
        self.scholarship = scholarship
        self.coe = coe
        self.cog = cog
