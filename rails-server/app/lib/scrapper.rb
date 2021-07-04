class Scrapper
  attr_reader :url, :scrapped_data

  def initialize
    @scrapped_data = []
    @url = "https://www.auchan.ro/store/%23profita/c/u50t0c0s0000"
  end

  def parse_url(url)
    unparsed_page = HTTParty.get(url)
    Nokogiri::HTML(unparsed_page)
  end


  def scrape
    parsed_page = parse_url(@url)

    parsed_page.css('.productGrid').children.each { |product| process_product(product) }

    print_data
  end

  def process_product(scrapped_product)
    title = scrapped_product.css('h2').text.squeeze(' ').strip

    return if title.blank?

    price = scrapped_product.css('span.big-price-multiple').text.strip.to_f

    scrapped_data << {
      title: title,
      price: price,
    }
  end

  def print_data
    @scrapped_data.each do |product|
      puts product.inspect
    end
  end
end