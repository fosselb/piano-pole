%Testing MPU-6050 module to determine position

clc;
close all;
clear;
format compact;

T = readtable('log.csv');

ax = table2array(T(:, 2));
ay = table2array(T(:, 3));
az = table2array(T(:, 4));

% use cumtrapz() for integration

% plot data
figure;
plot3(ax, ay, az, 'o');
title("Acceleration Data from MPU-6050 Module");
xlabel("Accel X (m/s^2)");
ylabel("Accel Y (m/s^2)");
zlabel("Accel Z (m/s^2)");