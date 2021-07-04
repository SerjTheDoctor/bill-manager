class UsersController < ApplicationController
  before_action :require_login
  before_action :require_self, only: :show

	def show
		user = User.find(params[:id])

    render json: user.permitted
	end

  def require_self
    render json: { errors: ['Unauthorized'] }, status: :unauthorized if current_user_id != params[:id].to_i
  end
end