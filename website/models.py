class Applicant:
    def __init__(self, key, email, name, school, program, year_level, noa_link, coe_link, financial_link, municipality=None):
        self.email = email
        self.key = key
        self.name = name
        self.municipality = municipality
        self.school = school
        self.program = program
        self.year_level = year_level
        self.noa_link = noa_link
        self.coe_link = coe_link
        self.financial_link = financial_link


class Student:
    def __init__(self, fName=None, lName=None, role=None, email=None, municipality=None, school=None, program=None, year_level=None, scholarship=None, status=None):
        self.fName = fName
        self.lName = lName
        self.role = role
        self.email = email
        self.municipality = municipality
        self.school = school
        self.program = program
        self.year_level = year_level
        self.scholarship = scholarship
        self.status = status


class Beneficiaries:
    def __init__(self, email, f_name, l_name, municipality, school, program, year_level, scholarship, coe, cog):
        self.email = email
        self.f_name = f_name
        self.l_name = l_name
        self.municipality = municipality
        self.school = school
        self.program = program
        self.year_level = year_level
        self.scholarship = scholarship
        self.coe = coe
        self.cog = cog


class Receipts:
    def __init__(self, key, date, amount, release_by):
        self.key = key
        self.date = date
        self.amount = amount
        self.released_by = release_by


class Admins:
    def __init__(self, f_name, l_name, email, role, status):
        self.f_name = f_name
        self.l_name = l_name
        self.email = email
        self.role = role
        self.status = status
