package moe.dazecake.autobanjimofang.Controller

import moe.dazecake.autobanjimofang.pojo.Result
import moe.dazecake.autobanjimofang.pojo.User
import moe.dazecake.autobanjimofang.service.UserService
import org.springframework.web.bind.annotation.CrossOrigin
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.web.bind.annotation.RestController
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStream
import java.io.InputStreamReader
import javax.annotation.Resource

@ResponseBody
@RestController
class UserController {
    @Resource
    lateinit var userService: UserService

    @CrossOrigin(origins = arrayOf("http://127.0.0.1:8000"))
    @PostMapping("/add")
    fun add(user: User): Result {
        return userService.add(user)
    }
}