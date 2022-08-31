from fileinput import filename
from fpdf import FPDF
from flask import Flask, render_template, request
import pickle
import numpy as np
import pyautogui
from geopy.geocoders import Nominatim
import webbrowser
from time import sleep
from PIL import Image
from itertools import product
import os
import matplotlib.image as image
import cv2
import numpy
import win32clipboard
import sys
import shutil
from operator import index
import glob
from flask import * 
from flask_mysqldb import MySQL
import pdfkit
