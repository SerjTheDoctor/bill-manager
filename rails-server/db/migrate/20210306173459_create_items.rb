class CreateItems < ActiveRecord::Migration[6.1]
  def change
    create_table :items do |t|
      t.integer :bill_id
      t.string :name
      t.string :unit
      t.float :unit_price
      t.float :quantity
      t.float :price

      t.timestamps
    end
  end
end
