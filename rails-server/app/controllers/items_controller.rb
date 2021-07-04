class ItemsController < ApplicationController
  before_action :require_login

  def index
    render json: Item.all
  end

  def create
    @item = Item.new(item_params)

    if @item.save
      render json: @item, status: :ok
    else
      render json: item_errors, status: :bad_request
    end
  end

  def update
    @item = Item.find(params[:id])

    if @item.update(item_params)
      render json: @item
    else
      render json: item_errors
    end
  end

  def destroy
    @item = Item.find(params[:id])
    @item.destroy

    render json: @item
  end

  def products
    name_query = params[:name]
    perm_keys = %i[id name unit]

    items = Item.where("items.name ilike ?", "%#{name_query}%")
                .includes(:bill)
                .order("bills.date desc")
                .references(:bill)

    products = items.map do |item|
      {
        id: item.id,
        name: item.name,
        unit: item.unit,
        unitPrice: item.unit_price,
        merchant: item.bill.merchant,
        date: item.bill.date
      }
    end

    render json: products
  end

  private

  def item_params
    params.require(:item).permit(:bill_id, :quantity, :unit, :unit_price, :price)
  end

  def item_errors
    @item.errors.full_messages.join(', ')
  end
end
