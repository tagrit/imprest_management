import frappe
from frappe.model.document import Document


class ImprestExpenseCategory(Document):
    def validate(self):
        """Validation before saving"""
        # Ensure expense account is set
        if not self.expense_account:
            frappe.throw("Please set an expense account for this category")
        
        # Validate account belongs to company
        account_company = frappe.db.get_value("Account", self.expense_account, "company")
        if account_company != self.company:
            frappe.throw(f"Account {self.expense_account} does not belong to company {self.company}")
        
        # Auto-generate category code if not set
        if not self.category_code:
            self.category_code = self.generate_category_code()
    
    def generate_category_code(self):
        """Generate a unique category code"""
        import re
        # Remove special characters and get first 3 letters
        code = re.sub(r'[^a-zA-Z0-9]', '', self.category_name)[:3].upper()
        
        # Check for uniqueness
        existing = frappe.db.count("Imprest Expense Category", {
            "category_code": ["like", f"{code}%"],
            "name": ["!=", self.name]
        })
        
        if existing > 0:
            code = f"{code}{existing + 1}"
        
        return code
