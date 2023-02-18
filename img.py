import requests
import xml.etree.ElementTree as ET
import zipfile
import os

def download_image(url, image_key):
    response = requests.get(url)

    if response.status_code == 200:
        return response.content, response.headers.get("Last-Modified"), response.headers.get("Content-Length")
    else:
        print(f"Failed to download image {image_key}.")
        return None, None, None

if __name__ == "__main__":
    bucket_name = input("Enter bucket name: ")
    prefix = input("Enter prefix (leave blank for all objects): ")
    output_file = input("Enter output zip file name: ")

    url = f"https://{bucket_name}.s3.amazonaws.com/?prefix={prefix}"
    response = requests.get(url)

    if response.status_code == 200:
        root = ET.fromstring(response.content)

        object_count = len(root.findall("{http://s3.amazonaws.com/doc/2006-03-01/}Contents"))
        print(f"Found {object_count} objects matching prefix '{prefix}' in bucket '{bucket_name}'.")

        proceed = input("Do you want to download all images? (yes/no): ")
        if proceed.lower() != "yes":
            print("Exiting script.")
            exit()

        image_keys = []
        for contents in root.iter("{http://s3.amazonaws.com/doc/2006-03-01/}Contents"):
            key = contents.find("{http://s3.amazonaws.com/doc/2006-03-01/}Key").text
            size = int(contents.find("{http://s3.amazonaws.com/doc/2006-03-01/}Size").text)

            # add the key and size to a list if the object is an image file
            if key.endswith(".jpg") or key.endswith(".jpeg") or key.endswith(".png"):
                image_keys.append((key, size))

        # sort the image keys based on size in descending order
        image_keys.sort(key=lambda x: x[1], reverse=True)

        with zipfile.ZipFile(output_file, mode="w") as zip_file:
            for key, size in image_keys:
                image_url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
                image_data, last_modified_date, image_size = download_image(image_url, key)

                if image_data is not None:
                    # add the image data to the zip file
                    zip_file.writestr(f"{key}.jpg", image_data)

                    # print the date of last modification and the size of the image
                    print(f"Image '{key}' downloaded successfully.")
                    print(f"Last Modified: {last_modified_date}")
                    print(f"Size: {image_size} bytes")

        # print the name, size, and location of the output zip file
        zip_file_size = os.path.getsize(output_file)
        print(f"All images matching prefix '{prefix}' downloaded and saved to '{output_file}'.")
        print(f"Zip file size: {zip_file_size} bytes")
        print(f"Zip file location: {os.path.abspath(output_file)}")
    else:
        print(f"Failed to list objects in bucket {bucket_name}.")