
import grpc
from generated import hello

def run():
  channel = grpc.insecure_channel('localhost:50051')
  stub = hello.GreeterStub(channel)
  response = stub.SayHello(hello.HelloRequest(name='you'))
  print("Greeter client received: " + response.message)
  response = stub.SayHelloAgain(hello.HelloRequest(name='you'))
  print("Greeter client received: " + response.message)


if __name__ == "__main__":
    run()