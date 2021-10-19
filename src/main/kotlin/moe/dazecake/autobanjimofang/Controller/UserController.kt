package moe.dazecake.autobanjimofang.Controller

import moe.dazecake.autobanjimofang.pojo.Result
import moe.dazecake.autobanjimofang.pojo.User
import org.springframework.web.bind.annotation.CrossOrigin
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.web.bind.annotation.RestController
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStream
import java.io.InputStreamReader

@ResponseBody
@RestController
class UserController {
    @CrossOrigin(origins = arrayOf("http://127.0.0.1:8000"))
    @PostMapping("/add")
    fun add(user: User): Result {
        var user: User = user
        var res: Result = Result()
        val cmd = arrayOf(
            "/bin/sh",
            "-c",
            "python3 /root/afk/Auto-banjimofang/python/login.py ${user.phone} ${user.passwd}"
        )
        try {
            //执行命令
            var p = Runtime.getRuntime().exec(cmd)
            //取得命令结果的输出流
            val fis: InputStream = p.getInputStream()
            //用一个读输出流类去读
            val isr = InputStreamReader(fis)
            //用缓冲器读行
            val br = BufferedReader(isr)
            var line: String? = null
            //直到读完为止
            while (br.readLine().also { line = it } != null) {
                println(line)
                if (line == "False") {
                    res.code = 401
                    res.msg = "登陆失败,请检查账号密码是否正确"
                } else if (line == "True") {
                    res.code = 200
                    res.msg = "登陆成功,已录入数据库"
                } else if (line == "Existing") {
                    res.code = 403
                    res.msg = "已经录入数据库,请勿重复录入"
                }
            }
        } catch (e: IOException) {
            e.printStackTrace()
        }

        return res
    }
}