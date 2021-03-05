from generated import hello

class Greeter(hello.GreeterServicer):

  def SayHello(self, request, context):
    return hello.HelloReply(message='Hello, %s!' % request.name)

  def SayHelloAgain(self, request, context):
    return hello.HelloReply(message='Hello again, %s!' % request.name)

