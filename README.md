# ElastiFace: AWS-based Adaptive Face Recognition

## Project Overview

ElastiFace is an innovative face recognition system deployed on AWS, showcasing custom autoscaling to efficiently handle varying demand. This project emphasizes rapid response, high accuracy, and secure data processing in a multi-tier cloud architecture.

## Features

- **Custom Autoscaling**: Dynamically scales App Tier instances from 0 to 20 based on real-time demand.
- **High Performance**: Achieves a 75% improvement in response times, supporting up to 1000 classifications per minute.
- **High Accuracy**: Delivers face recognition with an impressive 94% accuracy using state-of-the-art deep learning models.
- **Robust Data Handling**: Utilizes AWS S3 for persistent storage of input images and classification results.
- **Secure Communications**: Leverages AWS SQS for secure and reliable messaging between the Web Tier and App Tier.

## Tech Stack & Key Tools

- **Cloud Platform**: AWS EC2, AWS S3, AWS SQS
- **Programming Languages**: Python
- **Frameworks & Libraries**: Flask, Boto3, PyTorch, torchvision, torchaudio, MTCNN, InceptionResnetV1
- **Operating System**: Ubuntu (EC2 instances)
- **Version Control**: Git

## Setup & Deployment

1. **AWS Configuration**:
   - Set up EC2 instances with the required AMI for the Web Tier and App Tier.
   - Configure S3 buckets for input and output storage.
   - Set up SQS queues for request handling and response delivery.

2. **Environment Setup**:
   - Install Python and necessary libraries (Flask, Boto3, PyTorch) on EC2 instances.
   - Clone the project repository to the Web Tier EC2 instance.

3. **Running the Application**:
   - Start the Flask application on the Web Tier to listen on port 8000.
   - Deploy the deep learning model and autoscaling script on the App Tier instances.

4. **Testing**:
   - Utilize the provided workload generator to simulate user requests and validate the system's performance.

## Contributions

This project is open to contributions. Feel free to fork the repository, make improvements, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

---

Thank you for exploring ElastiFace, where dynamic scalability meets cutting-edge face recognition technology on AWS.

