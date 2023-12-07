local socket = require("socket")
math.randomseed(socket.gettime()*1000)
math.random(); math.random(); math.random()

local function get_detail()
    local method = "GET"
    local restaurant_name = "Chick-fil-A"
    -- local path = url .. "/get-detail?restaurant_name=" .. restaurant_name

    path = url .. "/post-detail?restaurant_name=Microsoft+Cafe&location=3785+Jefferson+Rd+NE&style=Stale+Food&capacity=100"
    local headers = {}
    return wrk.format(method, path, headers, nil)
end

request = function()
    cur_time = math.floor(socket.gettime())
    return get_detail(url)
end
