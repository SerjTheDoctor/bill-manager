class Example
	def self.run
		p "bills = Bill.all"
		bills = Bill.all

		p "count = bills.count"
		count = bills.count
		
		p "Found #{count} #{'bill'.pluralize(count)}"
	end
end