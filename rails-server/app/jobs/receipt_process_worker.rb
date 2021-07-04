require "uri"
require "net/http"

FLASK_URL = "#{ENV['IP']}:#{ENV['FLASK_PORT']}"

class ReceiptProcessWorker
    include Sidekiq::Worker
    sidekiq_options retry: 0

    def perform(bill_id)
        puts "Started processing bill with id #{bill_id}"
        
        bill = Bill.find(bill_id)
        bill.status = Bill::PROCESS_STATUS[:RUNNING]
        bill.save

        params = {
            path: bill.image_url
        }
        response = Net::HTTP.post_form(URI.parse("#{FLASK_URL}/receipts/path"), params)
        
        return if response.nil?

        puts "Response body: #{response.body}"
        bill.assign_data JSON.parse(response.body).symbolize_keys
        
        if bill.valid?
            bill.save
            puts "Bill is valid and saved!"
        else
            puts "Oups, we got a problem: #{bill.errors.messages.join(', ')}"
        end
    rescue => e
        puts "[ReceiptProcessWorker] ERROR: #{e}"
    
        return if bill.nil?

        bill.status = Bill::PROCESS_STATUS[:ERROR]
        bill.save
    end
end