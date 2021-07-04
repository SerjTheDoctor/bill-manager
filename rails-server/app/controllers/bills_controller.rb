class BillsController < ApplicationController
  before_action :require_login

  def index
    render json: Bill.where(user_id: current_user_id)
                     .includes(image_attachment: :blob)
                     .order(created_at: :desc, date: :desc)
                     .map(&:permitted)
  end

  def create
    create_bill_params = {
      image: params['image'],
      user_id: current_user_id,
      status: Bill::PROCESS_STATUS[:QUEUED]
    }

    bill = Bill.new(create_bill_params)

    if bill.save
      ReceiptProcessWorker.perform_async(bill.id)

      render json: Bill.first.permitted
    else
      render json: bill_errors, status: :bad_request
    end
  end

  def show
    bill = Bill.find(params[:id])

    if bill.user_id == current_user_id
      render json: bill.permitted(include_items: true)
    else
      render json: { errors: ['Unauthorized'] }, status: :unauthorized
    end
  end

  def update
    bill = Bill.find(params[:id])
    # byebug

    if bill.update(bill_params)
      params.require(:items).each do |pitem|
        pitem.permit!

        attrs = pitem.to_h
        attrs.except!(:unitPrice)
        attrs[:unit_price] = pitem[:unitPrice]

        item = Item.find(pitem[:id])
        item.assign_attributes(attrs)
        item.save
      end

      render json: bill.permitted(include_items: true)
    else
      render json: bill_errors
    end
  end

  def destroy
    bill = Bill.find(params[:id])
    bill.destroy

    render json: bill.permitted
  end

  private

  def bill_params
    params.require(:bill).permit(:id, :name, :status, :merchant, :price, :date)
  end

  def bill_errors
    @bill.errors.full_messages.join(', ')
  end
end
