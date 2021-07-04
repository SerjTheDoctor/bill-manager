class Item < ApplicationRecord
  belongs_to :bill

  def permitted
    perm_keys = %i[id name unit quantity price]
    sliced = self.slice(*perm_keys)
    {
      **sliced,
      unitPrice: self.unit_price
    }
  end
end
