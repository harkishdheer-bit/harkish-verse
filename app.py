from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from email.message import EmailMessage
import sqlite3
import os
import smtplib
from pathlib import Path
from functools import wraps
