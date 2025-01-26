class Finance:
    def __init__(self, credit_score, down_payment, loan_term, trade_in, vehicle_price=None):
        self.credit_score = credit_score
        self.down_payment = down_payment
        self.loan_term = loan_term
        self.trade_in = trade_in
        self.vehicle_price = vehicle_price 

    def loan_amount(self):
        return self.vehicle_price - self.down_payment - self.trade_in
        
    def monthly_pay(self, apr):
        total_loan = self.loan_amount()
        rate = apr / 12 / 100
        term = self.loan_term

        if rate == 0:
            return total_loan / term
        else:
            mp = (total_loan * rate * (1 + rate) ** term) / ((1 + rate) ** term - 1)
            if mp >= 0:
                return mp
            else:
                return 0
    

    def calc_apr(self):
        # Adjustment based on credit score
        if 300 <= self.credit_score <= 579:
            apr = 10  
        elif 580 <= self.credit_score <= 669:
            apr = 8  
        elif 670 <= self.credit_score <= 739:
            apr = 6  
        elif 740 <= self.credit_score <= 799:
            apr = 5 
        elif 800 <= self.credit_score <= 850:
            apr = 4 
        else:
            apr = 10  

        # Adjustment based on down payment 
        down_payment_percentage = self.down_payment / self.vehicle_price
        if down_payment_percentage >= 0.3:
            apr -= 1.5  
        elif down_payment_percentage >= 0.2:
            apr -= 1  

        # Adjustment based on trade in value
        trade_in_percentage = self.trade_in / self.vehicle_price
        if trade_in_percentage >= 0.2:
            apr -= 1  
        elif trade_in_percentage >= 0.1:
            apr -= 0.5  

        # Adjustment based on loan term
        if self.loan_term <= 36: 
            apr -= 1  
        elif self.loan_term >= 72: 
            apr += 1 

        # Adjustment based on loan amount
        loan_amount = self.loan_amount()
        if loan_amount >= 40000:
            apr += 1  
        elif loan_amount >= 25000:
            apr += 0.5  
        
        apr = max(apr, 3)

        return apr

    # Incorporate into point system
    def recommend_car(self):
        apr = self.calc_apr()
        monthly_payment = self.monthly_pay(apr)
        
        if monthly_payment <= self.desired_monthly:
            return f"You can afford this car! Monthly payment: ${monthly_payment:.2f}, APR: {apr}%"
        else:
            return f"Consider a less expensive car or adjusting the loan term. Monthly payment: ${monthly_payment:.2f}, APR: {apr}%"
