# Protecting-Legal-Documents
Web project developed for the subject of Cryptography that allows to encrypt the documents that are loaded using AES 128 bits, by means of Secret Sharing Scheme the key is divided into n parts being necessary k lawyers to decrypt the selected document again. The subkeys are encrypted with RSA and sent by telegram to the lawyers who share the same case. Digital certificates are created and sent by email.

The cryptographic services it offers are: authentication, confidentiality, non-repudiation and data integrity.

## Implemented with 💻
* [Django](https://www.djangoproject.com/) - The web framework used
* [Python](https://www.python.org/) - Programming language used
* [Bootstrap](https://getbootstrap.com/) - Multiplatform library for styles
