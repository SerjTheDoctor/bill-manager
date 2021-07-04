class CreateBills < ActiveRecord::Migration[6.1]
  def change
    create_table :bills do |t|
      t.integer :user_id
      t.string :name
      t.string :status
      t.string :merchant
      # t.string :image_url
      t.float :price
      t.date :date

      t.timestamps
    end
  end
end
