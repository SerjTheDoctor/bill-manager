class Bill < ApplicationRecord
  include Rails.application.routes.url_helpers

  has_many :items, dependent: :destroy
  belongs_to :user

  has_one_attached :image

  PROCESS_STATUS = {
    QUEUED: 'queued',
    RUNNING: 'running',
    PROCESSED: 'processed',
    ERROR: 'error'
  }

  def permitted(include_items = false)
    perm_keys = %i[id status date merchant price]
    sliced = self.slice(*perm_keys)

    sliced['items'] = self.items.order(id: :asc).map(&:permitted) if include_items

    {
      **sliced,
      name: title,
      imageUrl: image_url
    }
  end

  def title
    self.name || "#{self.date.strftime('%A')} at #{self.merchant.titleize}"
  rescue
    ""
  end

  def image_url
    return nil unless self.image.attached?
    
    rails_blob_url(self.image, disposition: "attachment")
  end

  def assign_data(params)
    self.status = PROCESS_STATUS[:PROCESSED]
    
    self.merchant = params[:store] if params[:store].present?
    self.date = Date.parse(params[:date]) rescue nil if params[:date].present?
    self.price = params[:total].to_f if params[:total].present?

    params[:items].reverse.each do |item|
      item.symbolize_keys!

      it = self.items.create(
        name: item[:name],
        quantity: item[:quantity].to_f,
        unit: item[:unit],
        unit_price: item[:unit_price].to_f,
        price: item[:total_price].to_f
      )
      puts "Created item #{it.name}"
    end
  end
end
