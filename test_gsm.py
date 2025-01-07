import machine
import utime

# Configuration for UART on Raspberry Pi Pico
uart_id = 0
baud_rate = 9600

# Initialize UART
uart = machine.UART(uart_id, baudrate=baud_rate, tx=machine.Pin(0), rx=machine.Pin(1))
print(f"UART initialized on UART{uart_id} with baud rate {baud_rate}")

# Send AT command and get response
def send_at_command(command, delay=2):
    uart.write(command + '\r\n')
    utime.sleep(delay)
    response = b''
    while uart.any():
        response += uart.read(1)
    return response

# Test sequence
def test_gsm_module():
    print("Testing GSM module...")

    # Test AT command
    print("Sending 'AT' command...")
    response = send_at_command('AT')
    print(f"Response to 'AT':\n{response}")

    # Check SIM status
    print("Checking SIM status with 'AT+CPIN?'...")
    response = send_at_command('AT+CPIN?')
    print(f"Response to 'AT+CPIN?':\n{response}")

    # Signal quality
    print("Checking signal quality with 'AT+CSQ'...")
    response = send_at_command('AT+CSQ')
    print(f"Response to 'AT+CSQ':\n{response}")

    # Network registration status
    print("Checking network registration with 'AT+CREG?'...")
    response = send_at_command('AT+CREG?')
    print(f"Response to 'AT+CREG?':\n{response}")

    # Operator name
    print("Getting operator name with 'AT+COPS?'...")
    response = send_at_command('AT+COPS?')
    print(f"Response to 'AT+COPS?':\n{response}")

if __name__ == '__main__':
    test_gsm_module()
