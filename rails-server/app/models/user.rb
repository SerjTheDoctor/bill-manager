class User < ApplicationRecord
  has_many :bills

  validates :email, format: { with: URI::MailTo::EMAIL_REGEXP } 

  has_secure_password

  def create_bill(merchant, price, date, name = nil)
    bills.create(
      name: name,
      status: Bill::PROCESS_STATUS[:QUEUED],
      merchant: merchant,
      # image_url: image_url,
      price: price,
      date: date
    )
  end

  def permitted
    self.slice(:id, :name, :email)
  end
end
