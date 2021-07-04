require "rack/multipart/parser" 

# Rack::Multipart::Parser.send :remove_const, :BUFSIZE 
# Rack::Multipart::Parser.const_set :BUFSIZE, 500_000