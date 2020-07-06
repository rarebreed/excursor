package app.khadga

import io.vertx.ext.web.client.WebClientOptions
import io.vertx.mutiny.core.Vertx
import io.vertx.mutiny.ext.web.client.WebClient

import org.eclipse.microprofile.config.inject.ConfigProperty
import javax.inject.Inject

class APIClient() {
    @ConfigProperty(name = "purecloud.hosts.api.name")
    lateinit var hostname: String

    @ConfigProperty(name = "purecloud.hosts.api.port")
    var port: Int = 443

    @Inject
    lateinit var vertx: Vertx

    val client: WebClient by lazy {
        WebClient.create(
            this.vertx,
            WebClientOptions()
                .setDefaultHost(this.hostname)
                .setDefaultPort(this.port)
                .setSsl(true)
                .setTrustAll(true)
        )
    }
}