local socket = require("socket")
math.randomseed(socket.gettime()*1000)
math.random();

local function generate_random_string(length)
    local charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    local random_str = ""
    for i = 1, length do
        local index = math.random(1, #charset)
        random_str = random_str .. charset:sub(index, index)
    end
    return random_str
end

local function req1()
    local method = "GET"
    local str = generate_random_string(10)  -- Generate a random string of length 10
    local path = "http://10.96.88.88:80/?key=" .. str
    
    local headers = {}
    return wrk.format(method, path, headers, nil)
end

local function req2()
    local method = "GET"
    local path = "http://10.96.88.88:80/?key=test1"
    local headers = {}
    return wrk.format(method, path, headers, nil)
end
  
request = function()
    -- ./wrk/wrk -d 30s -c 1 -t 1 http://10.96.88.88 -L -s ./config/samples /echo/echo.lua
    local req1_ratio  = 1
    local req2_ratio  = 1 - req1_ratio

    local coin = math.random()
    if coin < req1_ratio then
        return req1()
    else
        return req2()
    end
end