package ="index"
version ="0.1.0-1"
source = {
   url = "https://github.com/bcelabs/bce-sam-cli"
}

description ={
    summary       ="BSAM lua function hello world template",
    homepage      ="https://cloud.baidu.com/product/cfc.html",
    maintainer    ="bce-cfc-dev<bce-cfc-dev@baidu.com>",
    license       ="MIT"
}

dependencies ={    
    "lua-cjson == 2.1.0-1"
}

build ={
    type = "builtin",
    modules = {
        ["bsam.index"] = "index.lua",
    }
}